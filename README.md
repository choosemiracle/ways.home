# 同归 · WAYS HOME

**Different Paths · One Common Purpose**

从真、善、美、归出发的一张人类探索图谱。共同的方向是编辑与实践上的愿望，不是预先宣布所有传统拥有同一个答案。

## 本版结构

- `index.html`：叙事式首页、四个问题入口和核心专题导览。
- `atlas.html`：九条探索道路，可按主题与关键词组合筛选。
- `paths/*.html`：每条道路的独立阅读页，包含方法、检验、张力与相关路径。
- `questions/*.html`：真、善、美、归四个阅读入口。
- `encounters.html`：十二个历史与当代切面，可按地区或交流网络筛选。
- `unity.html`：十种不同语境的并读比较，选择可通过网址保留。
- `practice.html`：六种自愿的小练习，包含计时、暂停、书写、保存与导出。
- `essay.html`：网站的编辑立场与思想框架。
- `sources.html`：二十一项来源及研究、隐私和实践边界。
- `404.html`：不存在的路径返回页。

共 20 个内容页面，另有 1 个 404 页面。首批内容不声称覆盖全部人类思想或文化。

## 编辑与数据

内容在三个 JSON 文件中维护：

| 文件 | 用途 |
| --- | --- |
| `content/atlas.json` | 九条道路的完整文字与关联 |
| `content/chapters.json` | 四个主题、历史切面、比较条目、练习和论述 |
| `content/sources.json` | 来源、类型、链接与适用范围 |

有研究依据的段落使用 `refs` 引用来源 ID；原创解释和伦理判断明确标为“本站阐释”。每一个引用在生成时检查，链接到阅读室的对应条目。勿用一个引用为超出来源范围的论断背书。

`scripts/build.py` 是 HTML、搜索索引与网站地图的生成入口。不要手工修改生成的 HTML；请修改 JSON 或生成器，再重新构建。CSS 与浏览器脚本分别在 `styles.css` 和 `app.js` 中维护。

## 构建与预览

需要 Python 3.12+。网站本身不依赖 Node 或第三方浏览器框架。

```sh
python3 scripts/build.py
python3 scripts/serve.py --port 8785
```

预览地址：`http://127.0.0.1:8785/ways.home/`

预览服务器只绑定回环地址，不开放目录列表。网站从 `/ways.home/` 子路径加载，测试与 GitHub Pages 项目路径一致。

## 验证

Node 18+ 用于开发测试。仓库锁定测试依赖版本；自动化默认使用本机 Google Chrome，不读取用户浏览器资料。

```sh
npm ci
npm run build
npm run check
npm test
```

静态检查覆盖页面主标题、语言、重复 ID、本地文件和锚点、搜索索引。Playwright 覆盖 320 / 390 / 768 / 1440 像素下的所有页面，以及搜索、筛选、比较、计时、记录和无 JavaScript 阅读。

测试生成的 `preview-*.png`、`test-results/` 不提交到仓库。自动化验证不能替代内容审校、不同真实设备上的阅读体验或专业无障碍审计。

## 发布

仓库：`https://github.com/choosemiracle/ways.home`

GitHub Pages 项目地址：`https://choosemiracle.github.io/ways.home/`

本项目为直接提交生成页面的静态站。发布源应为 `main` 分支的根目录；`.nojekyll` 用来跳过 Jekyll 处理。同步代码与启用 Pages 是两件不同的事，部署后的状态以公开地址实际返回为准。旧 `gh-pages` 分支不由本构建流程维护。

## 隐私与实践

没有账号、统计脚本、广告或服务端笔记 API。全站搜索在浏览器中读取本地静态索引，不把查询发往第三方。

练习文字默认只在当前页面临时保留，主动点击保存才写入 `localStorage`。键名前缀为 `ways.home.notes.v1.`。这不是加密保险箱，存储也不是跨设备同步；共享设备应谨慎使用。读者可以导出文字或清除单项记录。

练习不是诊断、治疗、完整宗教修法或特殊体验承诺。随时可停止；边界、自主和问责，不因谈论“合一”而被取消。

> 天下同归而殊涂，一致而百虑。
