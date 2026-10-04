"""Semantic Chinese title composition shared by every generated page.

Editorial plans never alter copy. They provide clause and protected-phrase
boundaries; CSS chooses responsive line lengths. No-JS readers get the same markup.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

HEADING = re.compile(r'<h([123])\b([^>]*)>(.*?)</h\1>', re.S)
CLOSE_PUNCT = re.compile(r'^[，。！？；：、）》」』】\]\)]+$')

class TitleTypography:
    def __init__(self, root: Path):
        self.root = root
        self.plans = {}
        for number, line in enumerate((root/'content/heading-breaks.txt').read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            clauses = [part.split('|') for part in line.split('||')]
            if any(not unit or CLOSE_PUNCT.fullmatch(unit) for clause in clauses for unit in clause):
                raise ValueError(f'Invalid title unit, heading-breaks.txt:{number}')
            text = line.replace('|', '')
            if text in self.plans:
                raise ValueError(f'Duplicate title plan: {text}')
            self.plans[text] = clauses

    @staticmethod
    def plain(inner):
        return html.unescape(re.sub(r'<[^>]*>', '', inner))

    @staticmethod
    def core(text):
        match = re.search(r'\s*[↗→↑]$', text)
        return (text[:match.start()], text[match.start():]) if match else (text, '')

    def plan(self, text, inner=''):
        core, suffix = self.core(text)
        if core in self.plans:
            return self.plans[core], suffix, True
        # Existing intentional line breaks take precedence over a generic fallback.
        if re.search(r'<br\b', inner, re.I):
            parts = [self.plain(p) for p in re.split(r'<br\s*/?>', inner)]
            if ''.join(parts) == text:
                if suffix:
                    parts[-1] = parts[-1][:-len(suffix)]
                return [[p] for p in parts if p], suffix, False
        clauses = re.findall(r'[^，；：。！？]+[，；：。！？]*|[，；：。！？]+', core)
        return [[p] for p in clauses if p], suffix, False

    def compose(self, text, inner=''):
        clauses, suffix, reviewed = self.plan(text, inner)
        if ''.join(''.join(c) for c in clauses) + suffix != text:
            raise ValueError('Title text was changed during composition: '+text)
        output = []
        for i, clause in enumerate(clauses):
            units = []
            for j, unit in enumerate(clause):
                # Unknown future long phrases may wrap rather than overflow. Audits
                # require current long headings to have reviewed editorial plans.
                fallback = ' title-unit--fluid' if not reviewed and len(unit) > 9 else ''
                tail = suffix if i == len(clauses)-1 and j == len(clause)-1 else ''
                endmark = f'<span class="title-endmark" aria-hidden="true">{html.escape(tail)}</span>' if tail else ''
                units.append(f'<span class="title-unit{fallback}">{html.escape(unit)}{endmark}</span>')
            output.append('<span class="title-clause">'+'<wbr>'.join(units)+'</span>')
        return '<wbr>'.join(output)

    def format_document(self, document):
        def replace(match):
            level, attrs, inner = match.groups()
            text = self.plain(inner)
            if not text:
                return match.group(0)  # Dynamic image viewer gets a title on open.
            if 'title-flow' in attrs:
                return match.group(0)
            content = self.compose(text, inner)
            anchor = re.fullmatch(r'(<a\b[^>]*>)(.*?)(</a>)', inner, re.S)
            if anchor:
                content = anchor.group(1) + content + anchor.group(3)
            elif '<a' in inner:
                raise ValueError('Heading contains mixed anchors: '+inner)
            length = len(self.core(text)[0])
            size = 'long' if length >= 20 else 'medium' if length >= 13 else 'short'
            if 'class="' in attrs:
                attrs = attrs.replace('class="', f'class="title-flow title--{size} ', 1)
            else:
                attrs += f' class="title-flow title--{size}"'
            return f'<h{level}{attrs}>{content}</h{level}>'
        return HEADING.sub(replace, document)

    def build_runtime(self):
        template = (self.root/'scripts/heading-runtime.js').read_text(encoding='utf-8')
        compiled = template.replace('__HEADING_PLANS__', json.dumps(self.plans, ensure_ascii=False, separators=(',', ':')))
        (self.root/'assets/heading-layout.js').write_text(compiled, encoding='utf-8')
