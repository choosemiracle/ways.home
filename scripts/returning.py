"""A source-aware four-lens reading module and an entirely local workbook.

This is an editorial synthesis, not a developmental scale or spiritual test.
The shared generator owns typography, navigation, source numbering and search.
"""
import html


def esc(value):
    return html.escape(str(value), quote=True)


def home_entry(pre=''):
    return f'''<section class="shell return-invitation"><div><p class="eyebrow">回归之路 / FOUR LENSES</p><h2>把生命活出来，<br>也不被故事困住。</h2><p>认出热爱，形成表达，忠于生命，松开认同。不是四级台阶，而是面对同一件事时，可以反复往返的四种目光。</p></div><div><a class="button primary" href="{pre}returning.html">读懂四重视角 →</a><a class="text-link" href="{pre}returning/explore.html">带着一件事，开始探索 →</a><p class="small muted">不评分，不诊断，不替你决定使命。</p></div></section>'''


def build(g, data):
    lenses = data['lenses']
    for lens in lenses:
        for source in lens['refs']:
            if source not in g.SOURCES:
                raise ValueError('Unknown returning source: '+source)
    if len(lenses) != 4 or len({x['id'] for x in lenses}) != 4:
        raise ValueError('The workbook requires four distinct lenses')
    body = g.page_hero('回归之路 / FOUR LENSES','把生命活出来，也不被故事困住。','从热爱到表达，从聆听到放下证明自己的需要。带着同一件生活中的事，换四种目光再看一次。','归')
    body += '<section class="shell return-purpose"><p class="eyebrow">回归路上的宗旨 / 召集人的愿望</p><blockquote>' + ''.join('<span>'+esc(line)+'</span>' for line in data['manifesto']) + '</blockquote><p class="small muted">这是本模块的精神方向，不是要求来访者先接受的形上结论。“更少恐惧”不是不许害怕；“更多给予”也包括允许自己休息、接受与求助。</p></section>'
    body += '<section class="shell return-overview">' + g.heading('一件事 / 四重视角','不是更高，而是看得更完整。','四重视角是本站把不同思想放在一起使用的设计，不是四位作者共同提出的理论，也不是心理发展测量。可以从任何一处开始，随时回到前一问。')
    body += '<nav class="return-map" aria-label="四重视角">' + ''.join(f'<a href="#lens-{l["id"]}"><span class="return-glyph" aria-hidden="true">{l["glyph"]}</span><strong>{esc(l["name"])}</strong><span>{esc(l["question"])}</span><small>{esc(l["author"])}</small></a>' for l in lenses) + '</nav><p class="return-center">热爱 ⇄ 表达 ⇄ 忠实 ⇄ 松开<br><span>每一次，都回到关系与日常。</span></p>'
    body += g.note('这四种语言不能直接画等号','坎贝尔本来就谈到归来与超越自我，不是低阶起点；Dan Koe 的商业表达不等于终极身份；帕尔默的真实自我与课程的 Self 也处于不同语境。四者在这里相互提问，不相互取代。') + '</section>'
    body += '<div class="shell return-reading"><aside class="return-side"><p class="eyebrow">从你此刻开始</p><nav aria-label="本页阅读导航">'+''.join(f'<a href="#lens-{l["id"]}">{esc(l["name"])}</a>' for l in lenses)+'<a href="#purpose-not-status">用途，不是头衔</a><a href="#ordinary-cases">把视角放进一件事</a><a href="returning/explore.html">打开探索手记 →</a></nav></aside><div class="return-prose">'
    for l in lenses:
        body += f'''<section class="return-lens" id="lens-{l['id']}"><p class="eyebrow">{esc(l['author'])}</p><h2>{esc(l['name'])}</h2><h3 class="return-question">{esc(l['question'])}</h3><p>{esc(l['intro'])}</p><div class="return-source"><p class="return-phrase">{esc(l['phrase'])}</p><p class="small muted">{esc(l['phrase_note'])}</p><p>{esc(l['source_text'])}{g.refs(l['refs'])}</p></div><p><span class="editorial-label">本站的应用</span>{esc(l['reading'])}</p><dl class="return-discern"><div><dt>它打开什么</dt><dd>{esc(l['gift'])}</dd></div><div><dt>它可能怎样走偏</dt><dd>{esc(l['trap'])}</dd></div><div><dt>用什么重新校正</dt><dd>{esc(l['correction'])}</dd></div></dl><details class="return-prompts"><summary>停一下，带走一个问题</summary><ol>{''.join('<li>'+esc(p)+'</li>' for p in l['prompts'])}</ol><p><b>可以试的一小步：</b>{esc(l['action'])}</p></details><a class="text-link" href="returning/explore.html#reflect-{l['id']}">从这一问开始书写 →</a></section>'''
    body += f'''<section class="return-lens" id="purpose-not-status"><p class="eyebrow">再往深一处 / 目的，而非特殊身份</p><h2>让故事改变用途，不再索取身份。</h2><p>“上主之师”“老天的管道”“天主的使者”，可以表达愿意服务的心。但这几种语言不是不同传统中可直接互换的技术名词，也不意味着有人因此拥有不容质疑的权威。</p><p>《教师指南》第一节把重点放在一种选择：不再把自己的利益与他人的利益看成彼此分离。因此，更谨慎的读法是看见一次关系中的选择，而不是替自己取得一个神圣头衔。{g.refs(['return-teacher'])}</p><div class="return-purpose-pairs"><p><span>以前的用途</span>用经历证明我值得被看见，<br>或要求别人承认我是谁。</p><p><span>可以尝试的新用途</span>让经历帮助理解眼前的处境，<br>而不要求他人认领我的故事。</p></div><p class="editorial-label">本站的伦理约定</p><p>我可以说“我愿意被用于更多理解与给予”，同时继续核实事实、听取反馈、尊重拒绝，并为行为负责。越愿意服务，越不必自认替天发言；越能放下自我证明，越能允许别人不同意。</p><p>不执著故事，不等于没有故事；不把故事当成全部身份，也不等于否认伤害、事实或责任。第四问没有取消前三问，它使热爱和表达不必再承担证明整个人生价值的任务。</p><a class="text-link" href="studies/boundaries-return.html">延伸阅读：有时候，离开也是一种回归 ↗</a></section>'''
    body += '<section class="return-lens" id="ordinary-cases"><p class="eyebrow">本站假设案例 / 不是对你的判断</p><h2>同一件事，可以照见不同的问题。</h2>'
    for c in data['cases']:
        body += f'<details class="return-case"><summary>{esc(c["title"])}</summary><p>{esc(c["event"])}</p><ul>'+''.join('<li>'+esc(v)+'</li>' for v in c['views'])+'</ul><p class="return-case-move"><b>回到行动：</b>'+esc(c['move'])+'</p></details>'
    body += '<p>四问未必给出同一答案。热爱想扩大，身体可能需要缩小；表达需要边界，关系可能需要道歉。探索不是抹去这些张力，而是找一个你能负责、别人也有权回应的下一步。</p></section></div></div>'
    body += '<section class="shell return-start"><p class="eyebrow">把阅读交还给生活</p><h2>不用知道自己在哪一层，先看眼前这一件事。</h2><p>探索手记不会评分或分析你。它只帮助你记录四种目光，留下一项小行动、一条边界和一个复看时刻。空白也是允许的。</p>'+g.local_button('returning/explore.html','开始我的探索手记',True)+'</section>'
    g.page('returning.html','回归之路：热爱、表达、忠实与松开','从坎贝尔、Dan Koe、帕尔默与《奇迹课程》获得四重视角；保留区别，让表达服务于不特殊的目的。',body,'returning','探索模块')
    build_notebook(g, data)


def field(key,label,hint='',rows=3):
    return f'<div class="return-field"><label for="note-{key}">{esc(label)}</label>{f"<p id=\"hint-{key}\" class=\"small muted\">{esc(hint)}</p>" if hint else ""}<textarea id="note-{key}" name="{key}" data-return-field data-label="{esc(label)}" rows="{rows}" maxlength="12000"{f" aria-describedby=\"hint-{key}\"" if hint else ""} placeholder="写一点，或暂时留白。"></textarea></div>'


def build_notebook(g,data):
    pre='../'
    body=g.page_hero('探索手记 / REFLECTION','带着一件事，换四种目光。','不用先找到使命，也不用判断自己在哪一层。选择一件此刻能够承受的小事；可以跳过任何问题，只写一两句。','记','<a href="../returning.html">回归之路</a><span aria-hidden="true"> / </span>探索手记',pre)
    body+='<section class="shell return-notebook"><aside class="return-notebook-nav"><p class="eyebrow">自由往返</p><nav aria-label="手记导航"><a href="#event">此刻的事</a>'+''.join(f'<a href="#reflect-{l["id"]}">{esc(l["name"])}</a>' for l in data['lenses'])+'<a href="#next-step">回到日常</a><a href="#my-card" class="js-only">我的回归卡</a></nav><p class="small muted">约十五至二十分钟只是参考，不设倒计时，也不要求一次写完。</p><a class="text-link" href="../returning.html">先读四重视角</a></aside><div class="return-notebook-body">'
    body+=g.note('记录属于你','默认不保存、不上传，也不调用 AI 解读。只有主动保存，才写入当前浏览器；共享设备请谨慎使用。存储未加密，也不会跨设备同步。不要在这里填写他人的隐私。')
    body+='<form id="return-form" autocomplete="off"><section id="event" class="return-sheet"><p class="eyebrow">先把事实放在这里</p><h2>此刻，我想认真看一看什么？</h2>'+field('situation','我带来的这件事','先描述发生了什么，再分清自己的解释；不必书写最痛苦的经历。',4)+'</section>'
    for l in data['lenses']:
        body+=f'<section id="reflect-{l["id"]}" class="return-sheet" data-reflection="{l["id"]}"><p class="eyebrow">{esc(l["author"])}</p><h2>{esc(l["name"])}</h2><h3 class="return-question">{esc(l["question"])}</h3>'
        if l['id']=='release':
            body+='''<fieldset class="return-language"><legend>选择适合你的提问语言</legend><label><input type="radio" name="language" value="everyday" checked>日常语言</label><label><input type="radio" name="language" value="acim">《奇迹课程》语言</label></fieldset><div class="return-language-notes"><p class="small" data-release-language="everyday">不把暂时的解释当成全部事实：即使故事没有获胜，我仍能尊重什么、保护什么、给予什么？</p><details data-release-language="acim"><summary>《奇迹课程》的提问</summary><p class="small">我愿意把此刻的判断交给圣灵，学习不把我的利益与他人的利益看成分离吗？我愿意让这段经历服务于宽恕，而不把自己塑造成特别被选中的人吗？</p></details><p class="small muted">两种语言不是形上学上的等价翻译。选择课程语言只更换提示，不是宣告信仰；所有已写内容保持原样。不要求否认伤害或立刻和解。</p></div>'''
        body+='<ul class="return-open-questions">'+''.join('<li>'+esc(p)+'</li>' for p in l['prompts'])+'</ul>'+field(l['id'],l['field_label'])+'<p class="small muted">'+esc(l['correction'])+'</p></section>'
    body+='<section id="next-step" class="return-sheet"><p class="eyebrow">让探索接受生活的回应</p><h2>下一步要小，也要真实。</h2>'+field('action','我愿意尝试的一小步','写清什么时候、对谁、做什么；也可以是休息、求助或暂停一项承诺。',2)+field('boundary','需要保护的边界与责任','时间、能力、费用、他人的同意或安全；哪些事情现在不做？',2)+field('review','我准备何时复看，听取什么反馈','用可观察的经验复看，而不是给自己评修行等级。',2)+'</section></form>'
    body+='''<section class="return-card-tools"><p class="small muted">这些按钮只处理你写下的文字。回归卡是记录整理，不是测评结果、神谕或自动建议。</p><div class="actions js-only"><button type="button" class="button primary" id="return-preview">整理我的回归卡</button><button type="button" class="button" id="return-save">保存在此浏览器</button><button type="button" class="text-button" id="return-restore">读取本机记录</button><button type="button" class="text-button" id="return-export">导出文字</button><button type="button" class="text-button" id="return-clear">清除本模块记录</button></div><p id="return-status" class="small muted" role="status">当前仅在本页临时保留。</p><p class="no-js-note small">浏览器未启用脚本时仍可阅读、填写并自行复制，但保存和整理按钮不可用。离开本页前请自行保留文字。</p></section><section id="my-card" class="return-result" tabindex="-1" hidden><p class="eyebrow">你的原话 / 不附加判断</p><h2>我的回归卡</h2><p id="return-card-language" class="small muted"></p><dl id="return-card-content"></dl><p class="small muted">本次留白不代表没有进展。这张卡只记录此刻，不定义你是谁。</p></section>'''
    body+=g.note('随时可以停下','如果问题让你明显不适，可以停止书写，回到眼前环境并寻求可信任的支持。已有伤害或现实危机时，先处理安全与所需帮助，不用这份手记代替治疗、保护或专业判断。')+'</div></section>'
    g.page('returning/explore.html','探索手记：带着一件事，换四种目光','一份无评分的四重视角手记。可留白、主动本机保存、读取、导出与清除，形成属于自己的回归卡。',body,'returning','互动手记')
