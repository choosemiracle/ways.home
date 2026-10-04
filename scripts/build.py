#!/usr/bin/env python3
"""Build the complete, dependency-free static website from editorial JSON.

Run from any directory: python3 scripts/build.py
Generated HTML is committed and published through the existing gh-pages branch.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape
from enrichment import RichContent

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://choosemiracle.github.io/ways.home/"
SOURCES = json.loads((ROOT / "content/sources.json").read_text(encoding="utf-8"))
SOURCES.update(json.loads((ROOT / "content/sources-extra.json").read_text(encoding="utf-8")))
ROADS = json.loads((ROOT / "content/atlas.json").read_text(encoding="utf-8"))
CHAPTERS = json.loads((ROOT / "content/chapters.json").read_text(encoding="utf-8"))
DEPTH = json.loads((ROOT / "content/depth.json").read_text(encoding="utf-8"))
for road in ROADS:
    road['sections'].extend(DEPTH['road_updates'][road['id']]['sections'])
CHAPTERS['encounters'].extend(DEPTH['encounters'])
CHAPTERS['traditions'].extend(DEPTH['traditions'])
ROAD_BY_ID = {r["id"]: r for r in ROADS}
REF_NUM = {key: i + 1 for i, key in enumerate(SOURCES)}
LENSES = {q["id"]: q for q in CHAPTERS["questions"]}
PAGES: list[dict] = []
VERSION = hashlib.sha256(b"".join((ROOT / f).read_bytes() for f in ("styles.css", "app.js", "assets/enrich.css", "assets/enrich.js"))).hexdigest()[:10]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def prefix(path: str) -> str:
    return "../" * (len(Path(path).parts) - 1)


def refs(keys: list[str], pre: str = "") -> str:
    return "".join(f'<a class="citation" href="{pre}sources.html#{esc(k)}" title="{esc(SOURCES[k]["title"])}" aria-label="来源 {REF_NUM[k]}：{esc(SOURCES[k]["title"])}">[{REF_NUM[k]}]</a>' for k in keys)

RICH = RichContent(ROOT, SOURCES, DEPTH, refs)


def link(url: str, label: str, style: str = "text-link") -> str:
    return f'<a class="{style}" href="{esc(url)}">{label}<span aria-hidden="true"> ↗</span></a>'


def local_button(url: str, label: str, primary: bool = False) -> str:
    return f'<a class="button{" primary" if primary else ""}" href="{esc(url)}">{esc(label)}<span aria-hidden="true"> →</span></a>'


def heading(label: str, title: str, text: str = "") -> str:
    return f'<div class="section-heading"><p class="eyebrow">{esc(label)}</p><h2>{title}</h2>{f"<p>{esc(text)}</p>" if text else ""}</div>'


def note(title: str, text: str, dark: bool = False) -> str:
    return f'<aside class="note{" dark-note" if dark else ""}"><span class="eyebrow">{esc(title)}</span><p>{esc(text)}</p></aside>'


def page_hero(kicker: str, title: str, desc: str, char: str = "", crumb: str = "", pre: str = "") -> str:
    return f'''<div class="shell breadcrumb"><a href="{pre}index.html">同归</a><span aria-hidden="true"> / </span>{crumb or esc(kicker)}</div>
<section class="shell page-hero"><div><p class="eyebrow">{esc(kicker)}</p><h1>{esc(title)}</h1><p class="lead">{esc(desc)}</p></div>{f'<div class="chapter-glyph" aria-hidden="true">{esc(char)}</div>' if char else ''}</section>'''


def article_sections(sections: list[dict], pre: str) -> str:
    output = []
    for i, section in enumerate(sections, 1):
        source_ids = section.get("refs", [])
        badge = "阅读与辨析" if source_ids else "本站阐释"
        paragraphs = section['text'].split('\n\n')
        prose = ''.join('<p>'+esc(text)+(refs(source_ids,pre) if j==len(paragraphs)-1 else '')+'</p>' for j,text in enumerate(paragraphs))
        visual = RICH.image(section['image'],pre) if section.get('image') else ''
        visual += RICH.diagram(section['diagram']) if section.get('diagram') else ''
        output.append(f'''<section class="article-section" id="part-{i}"><p class="eyebrow">{i:02d} / {badge}</p><h2>{esc(section['title'])}</h2>{prose}{visual}</section>''')
    return "".join(output)


def toc(sections: list[dict]) -> str:
    return '<aside class="article-toc"><p class="eyebrow">这一页的线索</p><nav aria-label="本页目录">' + "".join(f'<a href="#part-{i}"><span>{i:02d}</span>{esc(s["title"])}</a>' for i, s in enumerate(sections, 1)) + '</nav><p class="small muted">带着一个问题读，<br>不必一次读完。</p></aside>'


def road_card(r: dict, pre: str = "", filtering: bool = False) -> str:
    tags = " ".join(r["tags"])
    searchable = " ".join([r["name"], r["en"], r["question"], r["intro"], *r["methods"]])
    attrs = f' data-road data-tags="{tags}" data-search="{esc(searchable)}"' if filtering else ""
    tag_labels = " · ".join(LENSES[k]["name"] for k in r["tags"])
    return f'''<article class="road-card"{attrs}><a class="road-main" href="{pre}paths/{r['id']}.html"><div class="road-top"><span class="eyebrow">{esc(r['en'])}</span><span class="small-glyph" aria-hidden="true">{esc(r['char'])}</span></div><h3>{esc(r['name'])}</h3><p>{esc(r['question'])}</p><span class="road-bottom"><span>{tag_labels}</span><b aria-hidden="true">↗</b></span></a></article>'''


def related_roads(ids: list[str], pre: str) -> str:
    return '<section class="related"><h2>从这里，继续相互参照</h2><div class="card-grid three">' + "".join(road_card(ROAD_BY_ID[k], pre) for k in ids) + '</div></section>'


def landscape() -> str:
    return '''<figure class="landscape"><svg viewBox="0 0 640 580" role="img" aria-labelledby="land-title land-desc">
<title id="land-title">山水之间，一条水流穿过层叠山势</title><desc id="land-desc">原创抽象山水。等高线般的山势与开阔水面并置，是路径与关系的视觉比喻，并非地理地图。</desc>
<defs><linearGradient id="land-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#839183" stop-opacity=".24"/><stop offset="1" stop-color="#839183" stop-opacity=".02"/></linearGradient><pattern id="paper-lines" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M0 24H24V0" fill="none" stroke="#738375" stroke-opacity=".06"/></pattern></defs>
<rect x="18" y="14" width="604" height="526" fill="url(#paper-lines)"/>
<circle cx="420" cy="122" r="54" fill="none" stroke="#a3794f" stroke-opacity=".45" stroke-width="1"/><circle cx="420" cy="122" r="47" fill="#c8ad76" fill-opacity=".1"/>
<path d="M0 277C60 299 97 211 154 210S225 287 289 235 361 183 408 230 521 139 640 158V500H0Z" fill="url(#land-fade)"/>
<path d="M0 337C65 295 109 348 168 315S243 242 300 287 372 335 447 286 544 241 640 278V540H0Z" fill="#6c8072" fill-opacity=".12"/>
<path d="M0 389C109 371 114 281 186 300S283 401 352 348 470 327 512 382 574 344 640 366V540H0Z" fill="#405f50" fill-opacity=".12"/>
<g fill="none" stroke="#526e5d" stroke-width="1" stroke-opacity=".46">
<path d="M0 277C60 299 97 211 154 210S225 287 289 235 361 183 408 230 521 139 640 158"/>
<path d="M0 289C62 311 99 223 156 222S227 299 291 247 363 195 410 242 523 151 640 170" opacity=".6"/>
<path d="M0 301C64 323 101 235 158 234S229 311 293 259 365 207 412 254 525 163 640 182" opacity=".3"/>
<path d="M0 337C65 295 109 348 168 315S243 242 300 287 372 335 447 286 544 241 640 278"/>
<path d="M0 350C65 308 109 361 168 328S243 255 300 300 372 348 447 299 544 254 640 291" opacity=".5"/>
<path d="M0 363C65 321 109 374 168 341S243 268 300 313 372 361 447 312 544 267 640 304" opacity=".25"/>
<path d="M0 389C109 371 114 281 186 300S283 401 352 348 470 327 512 382 574 344 640 366"/>
</g>
<path d="M291 313C258 356 443 375 364 424S226 472 247 542" fill="none" stroke="#f5f1e7" stroke-width="24"/>
<path class="river-line" d="M291 313C258 356 443 375 364 424S226 472 247 542" fill="none" stroke="#ad8860" stroke-width="1.2" stroke-opacity=".65"/>
<g stroke="#8e9e90" fill="none" stroke-opacity=".27"><path d="M32 474H178M401 474H579M40 489H161M423 489H606M24 504H172M391 504H564"/></g>
<g fill="#52685a" font-family="serif" font-size="13"><text x="42" y="64">各</text><text x="42" y="86">有</text><text x="42" y="108">来</text><text x="42" y="130">处</text></g>
<path d="M18 35V14H39M601 14H622V35M18 519V540H39M601 540H622V519" fill="none" stroke="#ad9b81"/>
</svg><figcaption><span>山水意象 · 路径的隐喻</span><span>各有来处，彼此相照。</span></figcaption></figure>'''


def page(path: str, title: str, description: str, body: str, active: str = "", kind: str = "专题") -> None:
    pre = '/ways.home/' if path == '404.html' else prefix(path)
    nav_items = [("index.html", "起点", "home"), ("atlas.html", "探索图谱", "atlas"), ("studies.html", "深读", "studies"), ("encounters.html", "文明交汇", "encounters"), ("unity.html", "合一诸义", "unity"), ("media.html", "视听", "media"), ("practice.html", "回到日常", "practice")]
    nav = "".join(f'<a href="{pre}{url}"{ " aria-current=\"page\"" if key == active else ""}>{label}</a>' for url, label, key in nav_items)
    doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f0e7">
<title>{esc(title)} · 同归 WAYS HOME</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{BASE_URL}{path}">
<meta property="og:title" content="{esc(title)} · 同归"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{BASE_URL}{path}">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{pre}styles.css?v={VERSION}"><link rel="stylesheet" href="{pre}assets/enrich.css?v={VERSION}"><script>document.documentElement.classList.add('js');</script><script src="{pre}app.js?v={VERSION}" defer></script><script src="{pre}assets/enrich.js?v={VERSION}" defer></script></head>
<body data-base="{pre}" data-page="{esc(path)}"><a class="skip-link" href="#main">跳到正文</a>
<header class="site-header"><div class="shell header-inner"><a class="brand" href="{pre}index.html" aria-label="同归首页"><span class="brand-seal" aria-hidden="true">归</span><span><b>同归</b><small>WAYS HOME</small></span></a>
<nav class="primary-nav" id="primary-nav" aria-label="主导航">{nav}</nav><div class="header-actions"><button class="icon-button js-only" data-search-open aria-label="搜索全站"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6.5"/><path d="m15 15 6 6"/></svg><span>搜索</span></button><button class="menu-button js-only" aria-expanded="false" aria-controls="primary-nav">目录</button></div></div></header>
<div class="reading-progress" aria-hidden="true"><span></span></div><main id="main">{body}</main>
<div class="shell end-nav"><a href="{pre}essay.html">关于同归</a><a href="{pre}sources.html">来源与边界</a><a href="{pre}studies.html">深读专题</a><a href="{pre}media.html">图像与视听</a><a href="{pre}applications.html">应用工坊</a><a href="#main" class="back-top">回到页首 ↑</a></div>
<footer class="site-footer"><blockquote>天下同归而殊涂，一致而百虑。</blockquote><p>《周易 · 系辞下》</p></footer>
<dialog class="search-dialog" id="search-dialog" aria-labelledby="search-title"><div class="dialog-head"><h2 id="search-title">在图谱中寻找</h2><button class="icon-button" data-search-close aria-label="关闭搜索">关闭 ×</button></div><label for="site-search" class="small">输入问题、传统或方法，例如“无我”“艺术”“边界”</label><input id="site-search" type="search" placeholder="你正在寻找什么？" autocomplete="off"><p class="small muted" id="search-status" role="status">搜索本站文章与来源，不查询外部网站。</p><div id="search-results" class="search-results"></div><p class="small muted search-tip">⌘ / Ctrl + K 打开搜索 · Esc 返回阅读</p></dialog>
{RICH.lightbox_dialog()}
</body></html>'''
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", "", body, flags=re.S)))
    PAGES.append({"url": path, "title": title, "description": description, "kind": kind, "text": re.sub(r"\s+", " ", text).strip()})


def build_home() -> None:
    gateways = "".join(f'''<a class="gateway" href="questions/{q['id']}.html"><span class="gateway-char" aria-hidden="true">{q['char']}</span><div><span class="eyebrow">{q['en']}</span><h3>{q['name']}</h3><p>{esc(q['title'])}</p></div><span class="gateway-arrow" aria-hidden="true">↗</span></a>''' for q in CHAPTERS["questions"])
    road_rows = "".join(f'''<a class="index-row" href="paths/{r['id']}.html"><span class="row-no">{i:02d}</span><div><h3>{r['name']}</h3><p>{esc(r['question'])}</p></div><span class="row-en">{r['en']}</span><span aria-hidden="true">↗</span></a>''' for i, r in enumerate(ROADS, 1))
    body = f'''<section class="shell home-hero"><div class="home-hero-copy"><p class="eyebrow">DIFFERENT PATHS · ONE COMMON PURPOSE</p><h1><span>殊途之间，</span><span>重新看见完整。</span></h1><p class="lead">从一首诗到一项实验，从独自沉思到共同生活，人类留下了许多探索的道路。我们怎样求真、向善、近美，又怎样在差异之中重新建立关系？</p><div class="actions">{local_button('#questions', '从一个问题开始', True)}{local_button('atlas.html', '打开探索图谱')}</div><p class="hero-caption">一张可以往返的地图，<br>不替任何传统预先决定它的终点。</p></div>{landscape()}</section>
<section class="shell gateway-section" id="questions">{heading('01 / 四个阅读坐标', '先从你真正关心的问题开始。', '真、善、美、归是同归的阅读视角，不是一份关于所有文明的统一答案。')}<div class="gateway-grid">{gateways}</div></section>
<section class="essay-band"><div class="shell essay-band-inner"><span class="vertical-note" aria-hidden="true">共同，并非相同</span><div><p class="eyebrow">同归的出发点</p><h2>保留差异之后，<br>我们怎样重新相遇？</h2><p>完整不必意味着取消边界。让科学保持严谨，让艺术拥有自由，让个人仍能说“不”，也让这些不同的声音不必彼此隔绝。</p>{link('essay.html','阅读：经过分化之后的连接')}</div><div class="relation-art" aria-hidden="true"><i></i><i></i><i></i><span>各自完整<br>仍有联系</span></div></div></section>
<section class="shell section route-index"><div class="index-intro">{heading('02 / 九种接近方式', '人类怎样展开探索？', '这些路径彼此重叠，也彼此质疑。每一页都从问题、方法、检验与边界展开。')}{local_button('atlas.html','按问题筛选')}</div><div class="index-rows">{road_rows}</div></section>
<section class="encounter-band"><div class="shell section"><div class="split-heading">{heading('03 / 文明交汇', '世界思想，<br>从来不止一个中心。', '从具体的文本、地点和知识实践进入；不把历史画成一条文明等级的阶梯。')}{link('encounters.html','沿十二个历史切面阅读')}</div><div class="encounter-preview"><a href="encounters.html#silk"><span class="eyebrow">欧亚交流</span><h3>思想也走过<br>海陆之间的路。</h3><p>知识在迁移与翻译中，获得新的解释。</p><span aria-hidden="true">↗</span></a><a href="encounters.html#timbuktu"><span class="eyebrow">西非 · 廷巴克图</span><h3>把另一座<br>知识之城放进地图。</h3><p>学习、文本与精神生活彼此交织。</p><span aria-hidden="true">↗</span></a><a href="encounters.html#living"><span class="eyebrow">美洲原住民</span><h3>活着的文化，<br>仍在表达自己。</h3><p>从当代的艺术、教育与生活听起。</p><span aria-hidden="true">↗</span></a></div><p class="small muted">历史入口的依据：{refs(['silk','timbuktu','native'])}</p></div></section>
<section class="shell section unity-teaser"><div class="large-glyph" aria-hidden="true">辨</div><div>{heading('04 / 合一诸义', '同一个词，<br>可能在说不同的事情。', '关系中的和谐、人格的整合、理论的统一与宗教中的不二，不在同一个层面。先辨明差别，再谈彼此照亮。')}{local_button('unity.html','选择两个入口并读',True)}</div></section>
<section class="shell practice-invitation"><div><span class="eyebrow">05 / 回到日常</span><h2>读过之后，<br>让一个小动作发生。</h2><p>辨认一次判断，听完一个人，或在一件作品前多停留三分钟。</p></div><div class="practice-invitation-links"><a href="practice.html#pause"><span>一分钟</span>先停一下 <b>→</b></a><a href="practice.html#look"><span>三分钟</span>重新观看 <b>→</b></a><a href="practice.html#listen"><span>六分钟</span>轮流聆听 <b>→</b></a></div></section>'''
    body = body.replace('<section class="shell section route-index">', RICH.home_feature()+'<section class="shell section route-index">')
    body = body.replace('沿十二个历史切面阅读','沿十五个历史切面阅读')
    page('index.html','人类探索的开放图谱','从真、善、美、归出发，阅读探索道路、深度论述与图像视频，再把问题带回日常实践。',body,'home','起点')


def build_atlas() -> None:
    filters = '<button type="button" data-lens="all" aria-pressed="true">全部</button>' + ''.join(f'<button type="button" data-lens="{k}" aria-pressed="false">{v["name"]}</button>' for k,v in LENSES.items())
    body = page_hero('探索图谱 / ATLAS','从问题出发，沿着路径深入。','九条路径是这张图谱的首批内容，不是互斥的学科分类，也不穷尽人类的探索。','途')
    body += f'''<section class="shell atlas-section"><div class="filter-toolbar js-only"><div class="filter-buttons" role="group" aria-label="阅读视角">{filters}</div><label class="filter-search">查找路径<input type="search" id="atlas-query" placeholder="名称、问题或方法"></label><button class="text-button" id="atlas-reset">重置</button></div><p class="small muted" id="atlas-count" role="status">共 9 条探索路径</p><div class="card-grid three" id="atlas-grid">{''.join(road_card(r, filtering=True) for r in ROADS)}</div><div id="atlas-empty" class="empty-state" hidden><h2>这组词暂时没有匹配。</h2><p>试试更简短的词，或清除筛选，重新看看九条路径。</p></div>{note('读图提示','筛选表示本站选择的阅读重点，不意味着其他路径与某种价值无关。科学也涉及美与责任，艺术也可以追问事实。')}</section>'''
    page('atlas.html','探索图谱','按真、善、美、归筛选九种人类探索方式。',body,'atlas','导航')
    for r in ROADS:
        pre = '../'
        crumb = '<a href="../atlas.html">探索图谱</a><span aria-hidden="true"> / </span>' + esc(r['name'])
        body = page_hero(r['en'],r['question'],r['intro'],r['char'],crumb,pre)
        body += '<div class="shell article-layout">' + toc(r['sections']) + '<article class="reading-column">'
        body += '<div class="method-strip">' + ''.join(f'<span>{esc(m)}</span>' for m in r['methods']) + '</div>'
        body += article_sections(r['sections'],pre)
        body += RICH.pathway_addon(r['id'],pre)
        body += f'''<section class="criteria-grid"><div><span class="eyebrow">怎样检验</span><p>{esc(r['knowledge'])}</p></div><div><span class="eyebrow">这里的回归</span><p>{esc(r['return'])}</p></div></section>'''
        body += note('需要保留的张力',r['tension'],True)
        body += f'<section class="article-section"><span class="eyebrow">本站设计 / 带回生活</span><h2>今天可以试的一件小事</h2><p>{esc(r["practice"])}</p>{local_button("../practice.html","进入日常练习")}</section></article></div>'
        body += '<div class="shell">' + related_roads(r['related'],pre) + '</div>'
        page(f'paths/{r["id"]}.html',r['name'],r['intro'],body,'atlas','探索道路')


def build_questions() -> None:
    for q in CHAPTERS['questions']:
        pre = '../'
        body = page_hero(q['name']+' / '+q['en'],q['title'],q['intro'],q['char'],pre=pre)
        body += '<div class="shell article-layout">' + toc(q['sections']) + '<article class="reading-column">' + article_sections(q['sections'],pre)
        body += note('一个值得保留的区别',q['tension'],True)
        body += f'<section class="article-section"><span class="eyebrow">一个随身问题</span><h2>把阅读带回今天</h2><p>{esc(q["practice"])}</p>{local_button("../practice.html","从一次小练习开始")}</section></article></div>'
        selected = [r['id'] for r in ROADS if q['id'] in r['tags']]
        body += '<div class="shell">' + related_roads(selected,pre) + '</div>'
        page(f'questions/{q["id"]}.html',q['name']+'：'+q['title'],q['intro'],body,kind='主题入口')


def build_encounters() -> None:
    body = page_hero('文明交汇 / ENCOUNTERS','许多地方，都在提出自己的问题。','这里选取十五个历史与当代切面：不是完整世界史，不是文明等级，也不把某个传统概括为一个静止的答案。','流')
    regions = list(dict.fromkeys(x['region'] for x in CHAPTERS['encounters']))
    options = '<option value="all">全部地区与网络</option>' + ''.join(f'<option value="{esc(r)}">{esc(r)}</option>' for r in regions)
    body += f'''<section class="shell encounter-section">{note('怎样阅读时间','有些节点是一处遗址，有些是一段漫长的解释传统。时间标签用于定位语境，不是在宣布思想的唯一起源。')}<div class="filter-toolbar js-only"><label>选择一个地区或交流网络<select id="region-filter">{options}</select></label><span class="small muted" role="status" id="encounter-count">{len(CHAPTERS['encounters'])} 个切面</span></div><div class="encounter-list">'''
    for i, e in enumerate(CHAPTERS['encounters'],1):
        visual=RICH.image(e['image']) if e.get('image') else ''
        body += f'''<article class="encounter-item" id="{e['id']}" data-region="{esc(e['region'])}"><div class="encounter-date"><span>{i:02d}</span><p>{esc(e['date'])}</p><small>{esc(e['region'])}</small></div><div><h2>{esc(e['title'])}</h2><p>{esc(e['text'])}{refs(e['refs'])}</p>{visual}<p class="encounter-insight"><span>由此提问</span>{esc(e['insight'])}</p></div></article>'''
    body += '</div>' + note('地图还没有画完','本版尚未系统展开犹太思想、耆那教、锡克教、伊斯兰科学史、东南亚与大洋洲诸传统等。遗漏不表示它们不重要；首批入口应继续接受补充和校正。') + '</section>'
    page('encounters.html','文明交汇','从十五个具体的文本、地点与知识实践，认识不同文化的探索与往返。',body,'encounters','历史切面')


def tradition_content(t: dict) -> str:
    return f'''<p class="eyebrow">{esc(t['name'])}</p><h3>{esc(t['term'])}</h3><dl>{''.join(f'<div><dt>{label}</dt><dd>{esc(t[key])}</dd></div>' for key,label in [('problem','它回应什么'),('practice','怎样实践'),('home','何谓回归'),('boundary','不能画等号的地方')])}</dl><p class="small">阅读依据 {refs(t['refs'])}</p>'''


def build_unity() -> None:
    ts = CHAPTERS['traditions']
    options = lambda selected: ''.join(f'<option value="{t["id"]}"{ " selected" if t["id"] == selected else ""}>{esc(t["name"])}</option>' for t in ts)
    body = page_hero('合一诸义 / DISTINCTIONS','先辨明差别，再谈彼此照亮。','“和谐”“共融”“不二”“整合”“统一”可以放在一起读，但不因此属于同一层面。这是一张比较用的读图表，不是传统的全部定义。','辨')
    body += f'''<section class="shell compare-section"><div class="split-heading">{heading('选两个入口并读','同样说“归”，究竟在说什么？')}<p class="small muted">比较是为了找出区别，不是判断谁更高级。</p></div><div class="compare-controls js-only"><label>左侧入口<select id="compare-left">{options('buddhist')}</select></label><button class="text-button" id="compare-swap" aria-label="交换两侧入口">交换 ⇄</button><label>右侧入口<select id="compare-right">{options('advaita')}</select></label></div><p class="small muted" id="compare-status" role="status"></p><div class="compare-grid"><article class="compare-card" id="compare-a">{tradition_content(ts[2])}</article><article class="compare-card" id="compare-b">{tradition_content(ts[3])}</article></div>{note('比较的限度','共用“问题—实践—回归”栏目，是本站提供的比较工具，不表示这些传统用相同方式定义自己。经验上的相近、概念上的相似和理论上的同一，应当分开讨论。')}</section><section class="shell section">{heading('十种不同的语境','保留每一种解释的边界。')}<div class="tradition-details">'''
    for t in ts:
        body += f'<details id="{t["id"]}"><summary><span>{esc(t["name"])}</span><strong>{esc(t["term"])}</strong><b aria-hidden="true">＋</b></summary><div class="tradition-body">{tradition_content(t)}</div></details>'
    body += '</div></section><div hidden id="tradition-templates">' + ''.join(f'<template data-tradition="{t["id"]}">{tradition_content(t)}</template>' for t in ts) + '</div>'
    body=body.replace('十种不同的语境','十四种不同的语境')
    body+='<section class="shell section">'+RICH.diagram('levels')+local_button('studies/one-and-many.html','深入阅读：我们说合一时在说什么')+'</section>'
    page('unity.html','合一诸义','并排比较十四种完整、联合、解脱与统一的语境，保留来源与区别。',body,'unity','比较')


def build_practice() -> None:
    body = page_hero('回到日常 / PRACTICE','今天，不必完成一整套理论。','留一点时间，做一次可停止、无需表现的小练习。这些是本站设计的一般性反思邀请，不是任何宗教的完整修法，也不是心理治疗。','行')
    body += '<section class="shell practice-page">' + note('先照顾自己的边界','练习始终自愿。可以睁眼、可以不写、可以提前结束；不要求特殊体验，也不要求透露隐私。有持续困扰或功能受损时，应寻求合格专业人士的帮助。') + f'<p class="small muted">关于专业心理支持的范围：{refs(["therapy"])}</p><div class="practice-grid">'
    for p in CHAPTERS['practices']:
        body += f'''<article class="practice-card" id="{p['id']}"><div class="road-top"><p class="eyebrow">{esc(p['label'])}</p><span class="small-glyph" aria-hidden="true">{p['char']}</span></div><h2>{esc(p['title'])}</h2><p>{esc(p['text'])}</p><ol>{''.join(f'<li>{esc(s)}</li>' for s in p['steps'])}</ol><p class="practice-prompt">{esc(p['prompt'])}</p><button class="button js-only" data-practice="{p['id']}" data-duration="{p['duration']}" data-title="{esc(p['title'])}" data-prompt="{esc(p['prompt'])}">打开计时与书写 →</button><p class="no-js-note small muted">关闭脚本时，可以自行计时，照着上面的步骤进行。</p></article>'''
    body += '''</div></section><dialog class="practice-dialog" id="practice-dialog" aria-labelledby="practice-title"><div class="dialog-head"><span class="eyebrow">留一段时间给此刻</span><button class="icon-button" id="practice-close">结束并返回 ×</button></div><h2 id="practice-title">先留一分钟</h2><p id="practice-question"></p><div class="timer-face" id="timer-face" aria-hidden="true">01:00</div><p id="timer-status" class="small" role="status">准备好了，再开始。</p><div class="timer-actions"><button class="button primary" id="timer-toggle">开始</button><button class="text-button" id="timer-reset">重新计时</button></div><div class="notes-area"><label for="practice-note">留下一点自己的记录</label><textarea id="practice-note" rows="4" placeholder="可以只写一句，也可以保持空白。"></textarea><p class="small muted">不会自动保存。点击保存后，只写入当前浏览器的网站存储，不上传；共享设备请谨慎使用，清理浏览器数据会丢失记录。</p><div class="note-actions"><button class="text-button" id="note-save">保存在此浏览器</button><button class="text-button" id="note-export">导出文字</button><button class="text-button" id="note-clear">清除此项记录</button></div><p id="note-status" class="small muted" role="status"></p></div></dialog>'''
    body+=RICH.applications_link()
    page('practice.html','回到日常','六种自愿、低强度的观察、聆听与书写练习，以及通往应用工坊的入口。',body,'practice','实践')


def build_essay() -> None:
    sections = CHAPTERS['essay']
    body = page_hero('关于同归 / EDITORIAL ESSAY','经过分化之后，重新学习连接。','这不是给人类历史预设的结局，而是同归选择的工作方向：让差异可以相遇，让每一种认识保留标准，也让生活不被切成彼此失联的碎片。','同')
    body += '<div class="shell article-layout">' + toc(sections) + '<article class="reading-column">' + article_sections(sections,'') + note('我们的共同目的','共同的方向不等于共同的形上学。减少伤害、认真求知、尊重差异与维护人的自主，是这里愿意承担的实践承诺。',True) + '</article></div>'
    page('essay.html','经过分化之后的连接','同归的编辑立场、历史叙述边界与共同生活的伦理方向。',body,kind='论述')


def build_sources() -> None:
    body = page_hero('来源与边界 / READING ROOM','每一种理解，都应当有来处。','这里区分原典、学术综述、机构研究与本站阐释。来源让论述可以被追问，而不是把某个名字变成不容质疑的权威。','读')
    body += '<section class="shell sources-page"><div class="policy-grid">'
    policies = [('事实与阐释分开','有出处的历史、概念论述附上编号。标为“本站阐释”的段落，是一种可被质疑的解释或伦理主张，不冒充原作者原话。深读中的假设案例与应用流程明确标为本站设计。'),('图像与视频保留来处','图像使用公共领域或馆方开放授权材料，保留署名、作品资料与使用依据。视频只引用原平台；中文导读不是字幕翻译。资料不能替代论证。'),('范围不冒充全貌','九条路径与十五个切面不是全部人类思想史。比较条目只代表明示语境；新增论述保留反对意见，不把框架写成已被证明的统一结论。'),('隐私与实践边界','本站无账号、无追踪统计，不上传练习文字。主动保存仅使用本浏览器。视频在读者同意后才连接外部平台，届时适用平台隐私规则。练习不提供诊断或疗效承诺。')]
    body += ''.join(f'<article><h2>{a}</h2><p>{b}</p></article>' for a,b in policies) + '</div>'
    body += f'<div class="filter-toolbar js-only"><label class="filter-search">查找阅读来源<input type="search" id="source-query" placeholder="标题、机构或关键词"></label><span class="small muted" id="source-count" role="status">{len(SOURCES)} 项来源</span></div><div class="source-list">'
    for k, s in SOURCES.items():
        searchable = ' '.join(str(v) for v in s.values())
        body += f'''<article id="{k}" class="source-entry" data-source data-search="{esc(searchable)}"><span class="source-number">{REF_NUM[k]:02d}</span><div><p class="eyebrow">{esc(s['type'])} / {esc(s['publisher'])}</p><h2><a href="{esc(s['url'])}" target="_blank" rel="noopener noreferrer">{esc(s['title'])}<span aria-hidden="true"> ↗</span></a></h2><p class="source-original">{esc(s['name'])}</p><p>{esc(s['note'])}</p></div></article>'''
    body += '</div><p id="source-empty" class="empty-state" hidden>没有匹配的来源。试试更简短的词。</p>' + note('关于原典与证据','圣经、古兰经等链接用于辨认文本本身及其语境，不作为科学或临床证据。研究综述也有范围与观点上的限制；与某个来源对话，不等于认可它的一切结论。') + '</section>'
    page('sources.html','来源与边界',f'{len(SOURCES)} 项阅读与视听来源、编辑原则、隐私说明与实践边界。',body,kind='阅读室')


def validate_content() -> None:
    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key,value in node.items():
                if key == 'refs':
                    for source_id in value:
                        if source_id not in SOURCES:
                            raise ValueError(f'Unknown source: {source_id}')
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(ROADS)
    walk(CHAPTERS)
    if len(ROAD_BY_ID) != len(ROADS):
        raise ValueError('Duplicate road ids')
    for r in ROADS:
        if not set(r['related']).issubset(ROAD_BY_ID):
            raise ValueError(f'Unknown related road: {r["id"]}')


def main() -> None:
    validate_content()
    (ROOT / 'assets').mkdir(exist_ok=True)
    (ROOT / 'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#f4f0e7"/><path d="M15 12v40h34V12zM24 20v24m7-24h10v24H31m0-12h10" fill="none" stroke="#925b40" stroke-width="3"/></svg>', encoding='utf-8')
    build_home()
    build_atlas()
    build_questions()
    build_encounters()
    build_unity()
    build_practice()
    build_essay()
    build_sources()
    RICH.build_all(sys.modules[__name__])
    search_pages = list(PAGES)
    (ROOT / 'assets/search-index.json').write_text(json.dumps(search_pages, ensure_ascii=False), encoding='utf-8')
    page('404.html','这里暂时没有这条路径','返回同归，重新选择一个入口。',page_hero('404 / 未找到页面','不妨换一条路。','这个地址没有对应页面，内容可能已经移动。','归',pre='/ways.home/')+'<div class="shell section"><a class="button primary" href="/ways.home/index.html">回到同归首页 →</a></div>')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{xml_escape(BASE_URL+p["url"])}</loc></url>' for p in search_pages) + '</urlset>'
    (ROOT / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (ROOT / 'assets/page-manifest.json').write_text(json.dumps([p['url'] for p in PAGES],indent=2),encoding='utf-8')
    print(f'Built {len(PAGES)} HTML pages, {len(SOURCES)} sources, {len(ROADS)} paths. Asset version: {VERSION}')


if __name__ == '__main__':
    main()
