"""Returning: shared practices, a distinct ACIM reading, and a private notebook.

The four practices are an editorial synthesis, not a developmental scale.
Stable notebook field names preserve version-1 records across reordered lenses.
"""
from __future__ import annotations

import html


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def paragraphs(text: str) -> str:
    return ''.join(f'<p>{esc(p)}</p>' for p in text.split('\n\n'))


def home_entry(pre: str = '') -> str:
    return f'''<section class="shell return-invitation"><div><p class="eyebrow">回归之路 / A PRACTICE OF RETURNING</p><h2>把生命活出来，<br>也不被故事困住。</h2><p>先照顾此刻，再辨认热爱、聆听生命、形成表达、松开认同。不是四级台阶，而是每次都能回到日常的四重功课。</p></div><div><a class="button primary" href="{pre}returning.html">进入回归之路 →</a><a class="text-link" href="{pre}returning/explore.html">带着一件事，开始探索 →</a><a class="text-link" href="{pre}returning/acim.html">另一个深入入口：《奇迹课程》 →</a><p class="small muted">不评分，不诊断，不替你决定使命。</p></div></section>'''


def artwork(g, key: str, question: str, note: str, pre: str = '') -> str:
    """Reuse licensed local originals; captions identify interpretation as our own."""
    image = g.RICH.images[key]
    return f'''<figure class="archive-figure return-artwork"><div class="archive-image"><a href="{pre}{image['file']}" data-lightbox aria-label="放大查看：{esc(image['title'])}"><img src="{pre}{image['file']}" alt="{esc(image['alt'])}" loading="lazy" decoding="async"><span class="enlarge-label" aria-hidden="true">放大观看 ↗</span></a></div><figcaption><div class="image-credit"><strong>{esc(image['title'])}</strong><span>{esc(image['creator'])} · {esc(image['date'])}</span><span>{esc(image['rights'])} · <a href="{esc(image['rights_url'])}" target="_blank" rel="noopener noreferrer">馆藏与使用依据 ↗</a>{g.refs([image['source']],pre)}</span></div><p class="image-question">{esc(question)}</p><p class="small muted">本站的观看邀请：{esc(note)} 不把作品当作本模块理论的证明。</p></figcaption></figure>'''


def foundation(g, data) -> str:
    f = data['foundation']
    support = ''.join(f'<article><h3>{esc(x["name"])}</h3><p>{esc(x["text"])}</p></article>' for x in f['supports'])
    return f'''<section class="shell return-foundation" id="foundation"><div class="return-grounding-copy"><p class="eyebrow">共同地基 / 随时可以回来</p><h2>{esc(f['title'])}</h2><p class="lead">{esc(f['intro'])}</p><div class="return-support-grid">{support}</div><p class="small muted">{esc(f['reference'])}{g.refs(f['refs'])}</p></div>{artwork(g,'pavilion','如果不必马上出发，此刻什么能让你安顿下来？','先看亭子、空处与水岸，再留意自己的反应。画面的安静不抹去它的历史处境。')}</section>'''


def route_map(lenses) -> str:
    cards = ''.join(f'''<a href="#lens-{l['id']}"><span class="return-glyph" aria-hidden="true">{l['glyph']}</span><strong>{esc(l['name'])}</strong><span>{esc(l['question'])}</span><small>{esc(l['author'])}</small></a>''' for l in lenses)
    return f'''<figure class="return-route-diagram"><figcaption><span>一处地基，四重功课，一个归来</span><small>本站的实践图，不是修行等级</small></figcaption><div class="return-route-ground"><b>安住此刻</b><span>身体 · 感受 · 关系 · 未知</span></div><nav class="return-map" aria-label="四重视角">{cards}</nav><div class="return-route-home"><b>每一次，都回到生活</b><span>承认 · 聆听 · 承担 · 接受</span><a href="#integration">看见可以观察的改变 →</a></div><p class="small muted">可以往返，可以跳过；有时先表达才听清自己，有时先停下才知道下一步。</p></figure>'''


def purpose_diagram() -> str:
    rows = [('热爱','让我成为特别的人','让我愿意参与，也照顾限度'),('表达','必须证明我不可替代','让所能回应具体需要'),('聆听','确认我的判断更高明','容许我的解释被修正'),('松开','成为超越别人的人','不再用故事给彼此定罪')]
    body = ''.join(f'<div class="purpose-row" role="row"><span class="purpose-form" role="rowheader">{a}</span><span role="cell">{b}</span><span role="cell">{c}</span></div>' for a,b,c in rows)
    return f'''<figure class="purpose-diagram" id="purpose-diagram"><figcaption><h3>形式不必更换，用途可以改变。</h3><small>本站情境图解，不是小我或圣灵的自动判定器</small></figcaption><div class="purpose-matrix" role="table" aria-label="同一形式的两种用途"><div class="purpose-labels" role="row"><span role="columnheader">同一形式</span><span role="columnheader">寻求自我证明</span><span role="columnheader">愿意重新学习</span></div>{body}</div><p>发现自己想被认可时，先看见，不必再补上一句“我真差”。</p></figure>'''


def acim_teaser(g) -> str:
    return '''<section class="return-lens return-acim-teaser" id="purpose-not-status"><p class="eyebrow">独立深入入口 / A COURSE IN MIRACLES</p><h2>同一段人生，重新学习观看。</h2><p>上主之师不是四重功课之后的奖章。“管道”或“使者”也不是不容质疑的权威。从课程来看，关键不仅是我怎样成为自己，还包括：我把眼前的人看成了谁？我正在让这件事服务于什么？</p><p>这个入口明确使用课程的神学语言，不要求所有来访者接受，也不将其他思想变成它的低阶版本。</p><a class="button primary" href="returning/acim.html">从《教师指南》继续阅读 →</a></section>'''


def build(g, data) -> None:
    lenses = data['lenses']
    if [l['id'] for l in lenses] != ['aliveness','fidelity','expression','release']:
        raise ValueError('Keep stable lens IDs and the reviewed reading order')
    def validate(node):
        if isinstance(node,dict):
            for key,value in node.items():
                if key == 'refs' and any(k not in g.SOURCES for k in value):
                    raise ValueError('Unknown returning source: '+str(value))
                validate(value)
        elif isinstance(node,list):
            for value in node: validate(value)
    validate(data)
    body = g.page_hero('回归之路 / A PRACTICE OF RETURNING','把生命活出来，也不被故事困住。','一处可以安住的地基，四重可以往返的功课。不是修成一个特别的自己，而是让所学进入真实的相遇。','归')
    body += '<nav class="shell return-section-nav" aria-label="选择阅读入口"><a href="#foundation">先安住</a><a href="#four-practices">四重功课</a><a href="#integration">回到日常</a><a href="returning/acim.html">课程视角</a><a href="returning/explore.html">我的手记</a></nav>'
    body += '<section class="shell return-purpose"><p class="eyebrow">回归路上的宗旨 / 召集人的愿望</p><blockquote>' + ''.join('<span>'+esc(line)+'</span>' for line in data['manifesto']) + '</blockquote><p class="small muted">这是精神方向，不是入场条件。更少恐惧，不是不许害怕；更少评判，不是放弃辨识；更多给予，也包括接受、休息与求助。</p></section>'
    body += foundation(g,data)
    body += '<section class="shell return-overview" id="four-practices">' + g.heading('四重功课 / 不再给人划分层级','不是更高，而是看得更完整。','这是本站的综合设计，不是四位作者共同提出的理论。先聆听再表达，是阅读上的安排，不是每个人必须遵循的生活次序。') + route_map(lenses)
    body += g.note('保留每一种思想的来处','坎贝尔本来就谈归来，Dan Koe 提供的是创作与事业的方法，帕尔默的真实自我与课程的 Self 不在同一语境。每位作者都可以帮助我们提问，却不必组成一条通向同一教义的阶梯。') + '</section>'
    body += '<div class="shell return-reading"><aside class="return-side"><p class="eyebrow">这一页的线索</p><nav aria-label="本页阅读导航">' + ''.join(f'<a href="#lens-{l["id"]}">{esc(l["name"])}</a>' for l in lenses) + '<a href="#ordinary-cases">放进一件事</a><a href="#integration">回到生活</a><a href="returning/acim.html">课程视角 →</a><a href="returning/explore.html">打开探索手记 →</a></nav></aside><div class="return-prose">'
    for l in lenses:
        body += f'''<section class="return-lens" id="lens-{l['id']}"><p class="eyebrow">{esc(l['author'])}</p><h2>{esc(l['name'])}</h2><h3 class="return-question">{esc(l['question'])}</h3><p>{esc(l['intro'])}</p><div class="return-source"><p class="return-phrase">{esc(l['phrase'])}</p><p class="small muted">{esc(l['phrase_note'])}</p><p>{esc(l['source_text'])}{g.refs(l['refs'])}</p></div><p><span class="editorial-label">本站的应用</span>{esc(l['reading'])}</p><dl class="return-discern"><div><dt>它打开什么</dt><dd>{esc(l['gift'])}</dd></div><div><dt>它可能怎样走偏</dt><dd>{esc(l['trap'])}</dd></div><div><dt>用什么重新校正</dt><dd>{esc(l['correction'])}</dd></div></dl><details class="return-prompts"><summary>停一下，带走一个问题</summary><ol>{''.join('<li>'+esc(p)+'</li>' for p in l['prompts'])}</ol><p><b>可以试的一小步：</b>{esc(l['action'])}</p></details><a class="text-link" href="returning/explore.html#reflect-{l['id']}">从这一问开始书写 →</a></section>'''
        if l['id'] == 'expression':
            body += '<section class="return-visual-pause"><p class="eyebrow">换一种方式，看看能力的用途</p>' + artwork(g,'astrolabe','一项精心练成的能力，怎样真正回应别人的需要？','从器物的刻度与结构观看具体能力，另问使用者的目的。宗教、艺术与测量的联系不等于互相替代。') + '</section>'
    body += acim_teaser(g)
    body += '<section class="return-lens" id="ordinary-cases"><p class="eyebrow">本站假设情境 / 可打开并读</p><h2>同一件事，可以照见不同的问题。</h2>'
    for c in data['cases']:
        body += f'<details class="return-case"><summary>{esc(c["title"])}</summary><p>{esc(c["event"])}</p><ul>' + ''.join('<li>'+esc(v)+'</li>' for v in c['views']) + '</ul><p class="return-case-move"><b>回到行动：</b>'+esc(c['move'])+'</p></details>'
    body += '<p>四问可能给出不同的提醒。热爱想扩大，身体可能需要缩小；表达需要勇气，关系可能需要道歉。探索不是抹去这些张力，而是找到能够负责的下一步。</p></section></div></div>'
    it = data['integration']
    body += '<section class="shell return-integration" id="integration">' + g.heading('共同归处 / 不是第五个等级',esc(it['title']),it['text']) + '<div class="return-fruit-grid">' + ''.join(f'<article><h3>{esc(s["name"])}</h3><p>{esc(s["text"])}</p></article>' for s in it['signs']) + '</div><p class="small muted">'+esc(it['note'])+'</p></section>'
    body += '<section class="shell return-start"><p class="eyebrow">把阅读交还给生活</p><h2>不用知道自己在哪一层，先看眼前这一件事。</h2><p>手记只整理你的原话，不评分、不判定使命。保留一项小行动、一条边界和一个复看时刻；空白也被允许。</p>' + g.local_button('returning/explore.html','开始我的探索手记',True) + '</section>'
    g.page('returning.html','回归之路：安住、聆听与真实表达','四重可以往返的功课，以身体、关系和现实责任为支撑；另设《奇迹课程》的深入观看入口。',body,'returning','探索模块')
    build_notebook(g,data)
    build_acim(g,data)


def field(key: str, label: str, hint: str = '', rows: int = 3) -> str:
    description = f'<p id="hint-{key}" class="small muted">{esc(hint)}</p>' if hint else ''
    aria = f' aria-describedby="hint-{key}"' if hint else ''
    return f'<div class="return-field"><label for="note-{key}">{esc(label)}</label>{description}<textarea id="note-{key}" name="{key}" data-return-field data-label="{esc(label)}" rows="{rows}" maxlength="12000"{aria} placeholder="写一点，或暂时留白。"></textarea></div>'


def release_prompt(g) -> str:
    return f'''<fieldset class="return-language"><legend>选择适合你的提问语言</legend><label><input type="radio" name="language" value="everyday" checked>日常语言</label><label><input type="radio" name="language" value="acim">《奇迹课程》语言</label></fieldset><div class="return-language-notes"><div data-release-language="everyday"><p>我不只是自己的故事，对方也不只是我给他的故事。此刻有哪些事实、边界和新的可能，需要一起保留？</p></div><details data-release-language="acim"><summary>《奇迹课程》的提问</summary><ol class="acim-notebook-prompts"><li>我正在要求这件事证明什么？</li><li>我把谁放到了与我分开的那一边？</li><li>我愿意把这个判断交给圣灵，接受另一种观看吗？</li><li>不要求对方改变来安慰我，我愿意怎样诚实回应？</li></ol><p class="small">看见自己又在评判，不必追加自我定罪。需要的是回来、修正，而不是假装已经不受影响。</p><p class="small">本站反思提示，不是课程标准练习。{g.refs(['return-purpose','return-correction','return-self'],'../')} <a class="text-link" href="acim.html">先读原典语境与应用边界 →</a></p></details><p class="small muted">切换只更换提示，不重写答案，也不表示两种语言在神学上等价。可以暂时不能宽恕；不要求否认伤害或立刻和解。</p></div>'''


def build_notebook(g,data) -> None:
    pre = '../'
    body = g.page_hero('探索手记 / REFLECTION','带着一件事，换四种目光。','先确认此刻能够承受，再选择一件小事。可以跳过，可以留白；这不是使命测验，也不是检验自己是否合格。','记','<a href="../returning.html">回归之路</a><span aria-hidden="true"> / </span>探索手记',pre)
    body += '<section class="shell return-notebook"><aside class="return-notebook-nav"><p class="eyebrow">自由往返</p><nav aria-label="手记导航"><a href="#grounding">先照顾此刻</a><a href="#event">此刻的事</a>' + ''.join(f'<a href="#reflect-{l["id"]}">{esc(l["name"])}</a>' for l in data['lenses']) + '<a href="#next-step">回到日常</a><a href="#my-card" class="js-only">我的回归卡</a></nav><p class="small muted">无需一次写完，也无需从头开始。</p><a class="text-link" href="../returning.html">先读四重功课</a></aside><div class="return-notebook-body">'
    body += g.note('记录属于你','默认不保存、不上传、不调用 AI。主动保存才写入本浏览器；记录不加密、不跨设备同步。旧版已保存手记仍可主动读取，不会自动展示或改写。')
    body += '<section class="notebook-grounding" id="grounding"><p class="eyebrow">不是一项需要通过的检查</p><h2>先照顾此刻，再开始提问。</h2><p>看看四周，留意坐着或站着的支撑。现在适合写一点吗？需要喝水、休息或找一个可信任的人吗？这些问题不要求答案，也不会被存储。</p><details><summary>今天没有热爱或答案，也可以。</summary><p>不用写最痛苦的经历。可以只记录一件需要照顾的小事，也可以合上页面，把今天还给生活。</p></details></section>'
    body += '<form id="return-form" autocomplete="off"><section id="event" class="return-sheet"><p class="eyebrow">先把事实放在这里</p><h2>此刻，我想认真看一看什么？</h2>' + field('situation','我带来的这件事','分开写事实、感受与解释；不要求寻找谁该受责备。',4) + '</section>'
    for l in data['lenses']:
        body += f'<section id="reflect-{l["id"]}" class="return-sheet" data-reflection="{l["id"]}"><p class="eyebrow">{esc(l["author"])}</p><h2>{esc(l["name"])}</h2><h3 class="return-question">{esc(l["question"])}</h3>'
        if l['id'] == 'release': body += release_prompt(g)
        body += '<ul class="return-open-questions">' + ''.join('<li>'+esc(p)+'</li>' for p in l['prompts']) + '</ul>' + field(l['id'],l['field_label']) + '<p class="small muted">'+esc(l['correction'])+'</p></section>'
    body += '<section id="next-step" class="return-sheet"><p class="eyebrow">让探索接受生活的回应</p><h2>下一步要小，也要真实。</h2>' + field('action','我愿意尝试的一小步','可以是澄清、道歉、兑现承诺，也可以是拒绝、休息或求助。',2) + field('boundary','需要保护的边界与责任','哪些事实、能力限制、他人的同意或安全，不能被一句“放下”取消？',2) + field('review','我准备何时复看，听取什么反馈','看看自己是否更诚实、更能聆听、更愿修正；不是给自己评修行等级。',2) + '</section></form>'
    body += '''<section class="return-card-tools"><p class="small muted">回归卡只整理你写下的文字，不作画像、判断或建议。修改阅读顺序不改变旧记录的字段含义。</p><div class="actions js-only"><button type="button" class="button primary" id="return-preview">整理我的回归卡</button><button type="button" class="button" id="return-save">保存在此浏览器</button><button type="button" class="text-button" id="return-restore">读取本机记录</button><button type="button" class="text-button" id="return-export">导出文字</button><button type="button" class="text-button" id="return-clear">清除本模块记录</button></div><p id="return-status" class="small muted" role="status">当前仅在本页临时保留。</p><p class="no-js-note small">浏览器未启用脚本时仍可阅读、填写并自行复制，但保存和整理按钮不可用。离开本页前请自行保留文字。</p></section><section id="my-card" class="return-result" tabindex="-1" hidden><p class="eyebrow">你的原话 / 不附加判断</p><h2>我的回归卡</h2><p id="return-card-language" class="small muted"></p><dl id="return-card-content"></dl><p class="small muted">本次留白不代表没有进展。这张卡只记录此刻，不定义你是谁。</p></section>'''
    body += g.note('随时可以停下','明显不适时先停止书写。伤害、胁迫或现实危机需要安全与合适支持；不以自省替代治疗、保护或专业判断。') + '</div></section>'
    g.page('returning/explore.html','探索手记：带着一件事，换四种目光','可留白、自由往返、主动保存的手记。保留旧记录，增加安住与关系中的观看，不评分、不上传。',body,'returning','互动手记')


def build_acim(g,data) -> None:
    acim = data['acim']
    body = g.page_hero('《奇迹课程》视角 / MANUAL FOR TEACHERS',acim['title'],acim['intro'],'照','<a href="../returning.html">回归之路</a><span aria-hidden="true"> / </span>课程视角','../')
    body += '<section class="shell acim-orientation"><p class="eyebrow">从本传统的语言进入 / 不是其他道路的终点</p><p>这一页使用“上主、圣灵、弟兄、救赎与宽恕”等课程语言。它们不只是一般心理技巧，也不代表所有灵修传统。你可以深入阅读，也可以返回通用入口。</p><div class="actions">' + g.local_button('../returning.html','返回四重功课') + g.local_button('explore.html?language=acim#reflect-release','带着一件事进入手记',True) + '</div></section>'
    body += '<section class="shell acim-visual-opening"><div><p class="eyebrow">先看一幅画 / 本站观看邀请</p><h2>同一幅画，先分清看见与解释。</h2><p>先说出画面中能指出的细节，再看看自己加上了什么故事。我们用它练习辨认解释，不把一幅日本版画说成课程教义的插图。</p><div class="acim-observation"><p><b>可以指出的细节</b>浪头、小船、船上的人，远处的山。</p><p><b>可能出现的解释</b>有人感到危险，有人感到壮阔，也有人先想到共同处境。</p><p><b>留给自己的问题</b>这些感受值得聆听，却是否已经告诉了我全部？</p></div></div>' + artwork(g,'wave','当注意力从浪头移向船上的人，什么改变了？','只改变观看的入口，不修改原图，也不替作者规定含义。','../') + '</section>'
    nav = ''.join(f'<a href="#acim-{s["id"]}">{esc(s["title"])}</a>' for s in acim['sections'])
    body += '<div class="shell return-reading"><aside class="return-side"><p class="eyebrow">逐节阅读</p><nav aria-label="课程专题目录">'+nav+'<a href="#acim-practice">带入一次相遇</a><a href="#acim-cases">情境对照</a></nav></aside><article class="return-prose acim-prose">'
    for s in acim['sections']:
        body += f'<section class="return-lens acim-section" id="acim-{s["id"]}"><p class="eyebrow">原典概述与本站应用</p><h2>{esc(s["title"])}</h2>' + paragraphs(s['text']) + '<p class="small">阅读依据 '+g.refs(s['refs'],'../')+'</p>'
        if s.get('diagram') == 'purpose': body += purpose_diagram()
        body += '</section>'
    body += '<section class="return-lens" id="acim-practice"><p class="eyebrow">本站反思提示 / 不替代原课练习</p><h2>同一次相遇，容许另一种回应。</h2><p>选一件能够承受的日常小事。无需判断自己是否配得上“上主之师”，也不强迫现在就感到宽恕。</p><div class="acim-practice-grid">' + ''.join(f'<article><span class="eyebrow">{esc(p["name"])}</span><p>{esc(p["question"])}</p></article>' for p in acim['practice']) + '</div><p class="acim-gentle-note">看见又在评判，是可以返回的地方，不是发现自己有罪的证据。</p>' + g.local_button('explore.html?language=acim#reflect-release','把这四问带入我的手记',True) + '</section>'
    body += '<section class="return-lens" id="acim-cases"><p class="eyebrow">本站假设情境 / 不是对读者的判断</p><h2>从抽象的宽恕，回到具体的一刻。</h2>'
    for c in acim['situations']:
        body += f'<details class="acim-case"><summary>{esc(c["title"])}</summary><dl>' + ''.join(f'<div><dt>{label}</dt><dd>{esc(c[key])}</dd></div>' for key,label in [('fact','可描述的事实'),('story','我加上的故事'),('opening','愿意重新观看'),('action','现实中的行动')]) + '</dl></details>'
    body += '</section><section class="return-lens" id="study-further"><p class="eyebrow">继续学习 / 不是一次理解就完成</p><h2>愿意选择，不等于已经完成训练。</h2><p>《教师指南》第4节谈到信赖等逐渐显出的品质，第16节也预设其所指教师已经学习练习手册。本站不据此设置等级或认证；一份导读不能替代完整学习，更不授予不可质疑的权威。'+g.refs(['return-qualities','return-training'],'../')+'</p><p>关于安全、同意、问责和专业帮助的提醒，是本站的实践伦理；不以这些提醒冒充课程全部形上教导，也不以教导免除现实责任。</p><a class="text-link" href="../sources.html#return-teacher">查看原典与来源 →</a></section></article></div>'
    body += '<section class="shell return-start acim-closing"><p class="eyebrow">本站的归纳 / 不是原典引文</p><h2>我不是自己的故事，你也不是我给你的故事。</h2><p>可以认真生活，认真创造，认真履行承诺；也可以让这些表达不再承担证明整个人生价值的任务。</p>' + g.local_button('../returning.html','回到四重功课') + '</section>'
    g.page('returning/acim.html','上主之师视角：同一段人生，重新学习观看','依据《教师指南》与练习手册，讨论共同利益、用途、观看的纠正、宽恕、接受与不再自我定罪。',body,'returning','课程专题')
