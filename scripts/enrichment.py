"""Rich editorial chapters: sourced images, consent-gated video and applied inquiry.

This module owns 4.0 supplements; build.py retains shared page and citation ownership.
Videos are referenced, never downloaded. All media markup exists without JavaScript.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


class RichContent:
    def __init__(self, root, sources, depth, cite):
        self.root = root
        self.sources = sources
        self.depth = depth
        self.cite = cite
        self.media = json.loads((root / 'content/media.json').read_text(encoding='utf-8'))
        self.workshops = json.loads((root / 'content/workshops.json').read_text(encoding='utf-8'))
        self.images = {item['id']: item for item in self.media['images']}
        self.videos = {item['id']: item for item in self.media['videos']}
        self.studies = {item['id']: item for item in self.depth['studies']}

    def image(self, key, pre='', compact=False):
        item = self.images[key]
        return f'''<figure class="archive-figure{' compact-figure' if compact else ''}"><div class="archive-image"><a href="{pre}{item['file']}" data-lightbox aria-label="放大查看：{esc(item['title'])}"><img src="{pre}{item['file']}" alt="{esc(item['alt'])}" loading="lazy" decoding="async"><span class="enlarge-label" aria-hidden="true">放大观看 ↗</span></a></div><figcaption><div class="image-credit"><strong>{esc(item['title'])}</strong><span>{esc(item['creator'])} · {esc(item['date'])}</span><span>{esc(item['rights'])} · <a href="{esc(item['rights_url'])}" target="_blank" rel="noopener noreferrer">来源与使用依据 ↗</a>{self.cite([item['source']],pre)}</span></div><p class="image-question">{esc(item['question'])}</p><p class="small muted">{esc(item['use'])}</p></figcaption></figure>'''

    def video(self, key, pre=''):
        item = self.videos[key]
        source = self.sources[item['source']]['url']
        direct = ('https://www.youtube.com/watch?v=' if item['provider']=='youtube' else 'https://vimeo.com/') + item['video']
        return f'''<article class="video-card" data-video-card><div class="video-intro"><p class="eyebrow">视听参照 / {esc(item['label'])}</p><h3>{esc(item['title'])}</h3><p>{esc(item['intro'])}</p><p class="video-attribution">{esc(item['original'])}<br>{esc(item['publisher'])}{self.cite([item['source']],pre)}</p></div><div class="video-stage" data-player-stage><div class="video-placeholder"><span class="play-symbol" aria-hidden="true">▷</span><span>先读导读，再决定是否播放。</span></div></div><div class="video-actions"><button class="button js-only" data-load-video data-provider="{item['provider']}" data-video-id="{item['video']}" data-video-title="{esc(item['title'])}">同意连接外部平台并载入</button><button class="text-button js-only" data-unload-video hidden>关闭播放器</button><a href="{esc(direct)}" target="_blank" rel="noopener noreferrer">原平台观看 ↗</a><a href="{esc(source)}" target="_blank" rel="noopener noreferrer">发布出处 ↗</a></div><p class="small muted video-privacy">默认不连接视频平台。点击载入后，平台会接收网络请求，并适用其隐私规则；不自动播放。英语原声，字幕以原平台为准；下文是本站中文导读，不是逐字译稿。</p><p class="small muted" data-video-status role="status">播放可能受地区、网络、平台或嵌入许可影响；文字导读不依赖视频。</p><div class="watch-guide"><div><span>观看线索</span><p>{esc(item['watch'])}</p></div><div><span>带着一个问题</span><p>{esc(item['question'])}</p></div><div><span>需要保留的区别</span><p>{esc(item['boundary'])}</p></div></div></article>'''

    def diagram(self,key):
        if key=='levels':
            rows=[('经验','我怎样感受到世界','第一人称描述，不自动证明宇宙结构。'),('关系','我们怎样共同生活','承诺、权利与责任，不要求取消差异。'),('解释','哪些规律连接现象','证据、模型与论证，不等于宗教救赎。'),('本体','什么存在，什么更基本','哲学命题，需要另外的理由与反对意见。')]
            return '<figure class="concept-diagram"><figcaption>四层读图法 <span>本站比较工具，不是传统自身的分类</span></figcaption><div class="level-grid">'+''.join(f'<div><b>{i:02d}</b><h3>{a}</h3><p>{b}</p><small>{c}</small></div>' for i,(a,b,c) in enumerate(rows,1))+'</div><p class="diagram-foot">经验上的相近 ≠ 理论上的同一；有差异 ≠ 不能合作。</p></figure>'
        if key=='governance':
            rows=[('使用','谁得到机会？','时段、进入条件、资源上限'),('维护','谁承担成本？','劳动、费用与实际责任'),('决定','谁能够发言？','知情、异议与正式权限'),('修正','失效后怎样改？','试行、反馈、复核与记录')]
            return '<figure class="concept-diagram"><figcaption>共同生活的四项检查 <span>本站原创案例分析</span></figcaption><div class="level-grid">'+''.join(f'<div><b>{i:02d}</b><h3>{a}</h3><p>{b}</p><small>{c}</small></div>' for i,(a,b,c) in enumerate(rows,1))+'</div><p class="diagram-foot">善意 → 具体安排 → 可观察后果 → 共同修正。不是一次讨论就完成的圆满。</p></figure>'
        raise ValueError('Unknown diagram: '+key)

    def study_card(self,key,pre='',illustrated=True):
        s=self.studies[key]
        photo=self.images[s['image']]
        image=f'<div class="study-cover"><img src="{pre}{photo["file"]}" alt="{esc(photo["alt"])}" loading="lazy" decoding="async"><small>{esc(photo["title"])}<br>{esc(photo["creator"])} · 详细使用依据见正文或视听室</small></div>' if illustrated else ''
        return f'<article class="study-card"><a href="{pre}studies/{key}.html">{image}<div class="study-card-copy"><p class="eyebrow">深读 / {esc(s["char"])}</p><h3>{esc(s["title"])}</h3><p>{esc(s["subtitle"])}</p><span class="text-link">进入六节论述 →</span></div></a></article>'

    def home_feature(self):
        return '<section class="shell section depth-home"><div class="split-heading"><div class="section-heading"><p class="eyebrow">深读与应用 / 在问题中继续深入</p><h2>不只知道有哪些路，<br>也理解它们怎样相遇。</h2><p>图像不是装饰，视频不是答案。沿着具体作品、论证与案例，把宏大的问题一点点说清楚。</p></div><a class="text-link" href="studies.html">阅读六篇深度专题 ↗</a></div><div class="study-grid">'+''.join(self.study_card(k) for k in ['evidence-meaning','seeing-art','shared-world'])+'</div><div class="edition-links"><a href="media.html">图像与视听：5 幅图像，6 段视频 →</a><a href="applications.html">应用工坊：4 套可导出流程 →</a></div></section>'

    def pathway_addon(self,road_id,pre):
        key=self.depth['road_updates'][road_id]['study']
        s=self.studies[key]
        return f'<section class="depth-bridge"><p class="eyebrow">继续深读 / 一个问题的展开</p><h2><a href="{pre}studies/{key}.html">{esc(s["title"])} ↗</a></h2><p>{esc(s["subtitle"])}</p><div class="actions"><a class="text-link" href="{pre}studies/{key}.html">阅读完整论述</a><a class="text-link" href="{pre}media.html#video-{s["video"]}">观看带导读的视频</a></div></section>'

    def lightbox_dialog(self):
        return '<dialog id="image-dialog" class="image-dialog" aria-labelledby="image-dialog-title"><div class="dialog-head"><h2 id="image-dialog-title">放大观看</h2><button class="icon-button" data-image-close>关闭 ×</button></div><img id="large-image" alt=""><div id="large-image-caption"></div></dialog>'

    def applications_link(self):
        return '<section class="shell applications-link"><p class="eyebrow">从个人练习，走向共同学习</p><h2>需要一套完整的活动流程？</h2><p>作品共读、分歧讨论、共同空间规则与跨知识学习，分别提供时间安排、产出和适用边界。</p><a class="button primary" href="applications.html">进入四套应用工坊 →</a></section>'

    def build_studies(self,g):
        body=g.page_hero('深读 / INQUIRY','把问题展开，直到它触及生活。','每一篇都包含具体材料、论证、反对意见与可继续追问的问题。本站主张不是最后答案；带着不同意见来读，同样有价值。','思')
        body+='<section class="shell study-index"><div class="study-grid">'+''.join(self.study_card(k) for k in self.studies)+'</div></section>'
        body+='<section class="shell section">'+g.heading('先分清，才连接','一张防止概念滑动的读图表。')+self.diagram('levels')+'</section>'
        body+='<section class="shell section glossary-section">'+g.heading('概念工具箱','十二个词，放回具体使用中。','这里给出便于阅读的工作解释，不是一套穷尽学术争议的词典。')+'<div class="glossary-grid">'
        for item in self.depth['glossary']:
            body+=f'<article><p class="eyebrow">{esc(item["en"])}</p><h3>{esc(item["term"])}</h3><p>{esc(item["text"])}{self.cite(item.get("refs",[]))}</p><p class="glossary-example">{esc(item["example"])}</p></article>'
        body+='</div></section>'
        g.page('studies.html','深读：从哲思到具体生活','六篇深度专题与十二个概念工具，讨论事实、意义、合一、艺术、制度、边界和知识对话。',body,'studies','深读导览')
        for key,s in self.studies.items():
            pre='../'
            crumb='<a href="../studies.html">深读</a><span aria-hidden="true"> / </span>'+esc(s['title'])
            body=g.page_hero('深读 / '+s['char'],s['title'],s['subtitle'],s['char'],crumb,pre)
            body+='<div class="shell article-layout">'+g.toc(s['sections'])+'<article class="reading-column">'
            body+=g.note('这一篇提出的主张',s['claim'])+g.article_sections(s['sections'],pre)
            body+=f'<section class="objection-box"><p class="eyebrow">不要跳过反对意见</p><h2>{esc(s["objection"])}</h2><p>{esc(s["reply"])}</p><small>以上是本站的论证与回应，不是关于争议已经终结的声明。</small></section>'
            body+='<section class="follow-questions"><h2>把问题带到下一次相遇</h2><ol>'+''.join(f'<li>{esc(q)}</li>' for q in s['questions'])+'</ol></section>'
            body+=self.video(s['video'],pre)
            if not any(section.get('image')==s['image'] for section in s['sections']):
                body+='<section class="visual-return"><p class="eyebrow">换一个入口，再看一次</p>'+self.image(s['image'],pre)+'</section>'
            related_workshops=[w for w in self.workshops if w['study']==key]
            if related_workshops:
                body+='<section class="depth-bridge"><h2>让阅读成为一次共同学习</h2>'+''.join(f'<p><a class="text-link" href="../applications.html#{w["id"]}">{esc(w["title"])} · {w["duration"]} 分钟 →</a></p>' for w in related_workshops)+'</section>'
            body+='</article></div><div class="shell">'+g.related_roads(s['paths'],pre)+'</div>'
            g.page(f'studies/{key}.html',s['title'],s['subtitle'],body,'studies','深读专题')

    def build_media(self,g):
        body=g.page_hero('图像与视听 / MEDIA','让材料本身，也有说话的机会。','五幅可追溯的图像，六段来自作者、大学或研究机构的参考视频。每一项都配有中文问题与解释边界；不必能播放视频，才能继续阅读。','看')
        body+='<section class="shell media-room">'+g.note('进入之前','图片来自公共领域或馆方开放授权记录，并保留署名与使用依据。视频只引用原发布平台：不会下载、转载或自动连接。点击载入后，网络访问适用外部平台规则。')
        body+='<div class="filter-toolbar js-only"><div class="filter-buttons" role="group" aria-label="资料类型"><button data-media-kind="all" aria-pressed="true">全部</button><button data-media-kind="image" aria-pressed="false">图像</button><button data-media-kind="video" aria-pressed="false">视频</button></div><label class="filter-search">查找资料<input id="media-query" type="search" placeholder="作者、作品或提问"></label><button class="text-button" id="media-reset">重置</button></div><p class="small muted" id="media-count" role="status">11 项图像与视听资料</p><div class="media-grid">'
        for item in self.images.values():
            search=' '.join(str(item[k]) for k in ['title','creator','question','use'])
            body+=f'<div class="media-item" id="image-{item["id"]}" data-media-item data-kind="image" data-search="{esc(search)}">'+self.image(item['id'])+'</div>'
        for item in self.videos.values():
            search=' '.join(str(item[k]) for k in ['title','publisher','intro','question','original'])
            body+=f'<div class="media-item" id="video-{item["id"]}" data-media-item data-kind="video" data-search="{esc(search)}">'+self.video(item['id'])+'</div>'
        body+='</div><div class="empty-state" id="media-empty" hidden>没有匹配资料。可换一个词，或重置类型筛选。</div>'+g.note('字幕、网络与时间','资料链接与元数据在 2026 年 10 月 5 日核对。视频为英语原声，原平台是否提供中文字幕可能变化；本站中文导读不是字幕翻译。网络、地区或嵌入许可也可能导致无法播放。')+'</section>'
        g.page('media.html','图像与视听','五幅真实图像、六段机构或作者视频，附中文导读、开放问题与版权来源。',body,'media','视听室')

    def build_applications(self,g):
        body=g.page_hero('应用工坊 / APPLICATIONS','把哲思变成一场有边界的共同学习。','四套本站原创流程，适用于普通学习与日常协作。它们不是疗法、完整宗教修法或经过验证的效果保证；使用前先确认参与自愿及实际权限。','行')
        body+='<section class="shell applications-page"><nav class="workshop-jumps" aria-label="选择应用流程">'+''.join(f'<a href="#{w["id"]}"><span>{w["duration"]} 分钟</span>{esc(w["title"])}</a>' for w in self.workshops)+'</nav>'
        for w in self.workshops:
            minutes=0
            timeline=''
            for step in w['steps']:
                end=minutes+step['minutes']
                timeline+=f'<li><span class="step-time">{minutes:02d}—{end:02d} 分</span><div><h3>{esc(step["title"])}</h3><p>{esc(step["text"])}</p></div></li>'
                minutes=end
            body+=f'<article class="workshop" id="{w["id"]}" data-workshop><p class="eyebrow">本站原创流程 / {esc(w["audience"])}</p><div class="workshop-title"><h2>{esc(w["title"])}</h2><span>{w["duration"]} 分钟</span></div><p class="lead">{esc(w["focus"])}</p><div class="workshop-controls js-only"><button class="button" data-export-plan="{w["id"]}">导出完整流程 .md ↓</button><button class="text-button" data-print-plan>打印此流程</button><span data-plan-status class="small muted" role="status"></span></div><div class="plan-material"><span class="eyebrow">准备材料</span><p>{esc(w["material"])}</p><div class="actions"><a class="text-link" href="studies/{w["study"]}.html">对应深读文章 ↗</a><a class="text-link" href="media.html#video-{w["video"]}">视频与中文导读 ↗</a></div></div>'
            if w.get('image'): body+=self.image(w['image'],compact=True)
            body+='<ol class="workshop-timeline">'+timeline+'</ol><div class="plan-questions"><h3>可选的开放问题</h3><ul>'+''.join(f'<li>{esc(q)}</li>' for q in w['questions'])+'</ul></div><div class="plan-outcomes">'+''.join(f'<div><span class="eyebrow">{label}</span><p>{esc(w[key])}</p></div>' for key,label in [('output','具体产出'),('boundary','适用边界'),('review','怎样复盘')])+'</div></article>'
        body+=g.note('先判断适不适合','存在暴力、胁迫、危机或显著权力不对等时，不要用普通对话流程要求当事人面对面解决。优先安全与合适支持。针对真实组织的规则，讨论草案不等于获得正式授权。')+'</section>'
        g.page('applications.html','应用工坊','四套可导出和打印的原创学习流程，含时间安排、资料、问题、产出与边界。',body,'practice','应用')
        (self.root/'assets/workshops.json').write_text(json.dumps(self.workshops,ensure_ascii=False),encoding='utf-8')

    def validate(self):
        for key,s in self.studies.items():
            if s['image'] not in self.images or s['video'] not in self.videos:
                raise ValueError('Unknown media for study '+key)
        for item in self.media['images']:
            if not (self.root/item['file']).is_file():
                raise ValueError('Run scripts/fetch_media.py for '+item['file'])
            if not all(item.get(k) for k in ['alt','rights','rights_url','creator']):
                raise ValueError('Missing image attribution '+item['id'])
        for item in self.media['videos']:
            pattern=r'[A-Za-z0-9_-]{11}' if item['provider']=='youtube' else r'[0-9]+'
            if item['provider'] not in ('youtube','vimeo') or not re.fullmatch(pattern,item['video']):
                raise ValueError('Invalid video '+item['id'])
        for w in self.workshops:
            if sum(s['minutes'] for s in w['steps']) != w['duration']:
                raise ValueError('Workshop duration mismatch '+w['id'])
            if w['study'] not in self.studies or w['video'] not in self.videos:
                raise ValueError('Unknown workshop reference '+w['id'])
        def walk(node):
            if isinstance(node,dict):
                for k,v in node.items():
                    if k=='refs':
                        for source in v:
                            if source not in self.sources: raise ValueError('Unknown source '+source)
                    if k=='source' and isinstance(v,str) and v not in self.sources:
                        raise ValueError('Unknown media source '+v)
                    walk(v)
            elif isinstance(node,list):
                for item in node: walk(item)
        walk(self.depth)
        walk(self.media)

    def build_all(self,g):
        self.validate()
        self.build_studies(g)
        self.build_media(g)
        self.build_applications(g)
