# 项目设计方向

[首页](../README.md) · [阅读方式](reading.md) · [知识关联](../knowledge/index.md)

**知识库的关联能力 + 文档站的清晰界面 + 大学课程资料的组织方式 + 脑图与关系图。** 日常学习以 VS Code 与 GitHub 中的 Markdown 为入口，网站提供额外的阅读视图。

| 参考方向 | 借鉴什么 | 本项目怎样采用 |
|---|---|---|
| [Quartz](https://quartz.jzhao.xyz/) / [Starlight](https://starlight.astro.build/) 的知识库能力 | Quartz 的笔记关联、图谱和搜索；Starlight 的文档导航、搜索与多语言阅读 | 学期导航、跨课程概念关联、中俄资料搜索与[反向关联](../knowledge/backlinks.md)，从笔记回到引用它的页面 |
| [Fumadocs](https://www.fumadocs.dev/) 的现代 UI | 清晰的层级、留白、目录与搜索入口 | 课程卡片、清晰的留白、状态标签、响应式导航与深浅色阅读界面 |
| [ZJU](https://github.com/QSCTech/zju-icicles) / [HITSZ](https://hoa.moe/) 的课程资料结构 | ZJU 的课程目录与目录 README；HITSZ 的年份、专业导航 | 按学期找到课程，再在同一份课程 `readme.md` 中查看讲座、笔记、实验、通过状态和复习资料；保留原代码与报告目录 |
| [Markmap](https://markmap.js.org/) 的脑图 | 把 Markdown 标题层级转成可展开的脑图 | 已加入[复习脑图](../knowledge/mindmap.md)：网站支持展开、收起与缩放，另有可双击打开的离线 HTML；VS Code / GitHub 使用同一份 Markdown 大纲 |
| [Mermaid](https://mermaid.js.org/) 的知识可视化 | 用文本描述概念关系、流程和结构 | [知识关联](../knowledge/index.md)中已有 Mermaid 图，与表格里的真实笔记、实现和答辩资料相连 |

课程目录只保留一份课程入口 `readme.md`，将原有讲座归类、实验链接、通过记录与新增导航合并在一起。`cheatsheet.md`、`quick-review.md` 等有独立学习内容的文件继续保留。

课程与实验统一使用 **✓ 已通过 / ○ 待通过 / — 未标记**。第 1–4 学期已全部通过；第 5 学期的课程与实验按当前记录维护。实验表可直接修改状态列，重新生成时保留。

以上方向已落实为课程资料结构、现代阅读界面、资料反向关联、Markmap 脑图与 Mermaid 知识图。网站继续使用现有 VitePress，原始 Markdown 保持为唯一资料来源。
