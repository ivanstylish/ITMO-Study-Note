# 在 VS Code 与 GitHub 阅读

[首页](../README.md) · [按学期](index.md) · [按课程](courses.md) · [考试复习](../study/revision.md) · [实验答辩](../study/defense.md)

所有学习入口都是仓库内的 Markdown 文件。日常查阅不需要启动网站、运行 npm 或打开任何辅助应用；直接打开仓库的 `README.md` 就能进入学期、课程、知识点、速查和答辩。

## VS Code：打开资料就能用

1. 在 VS Code 打开平时使用的项目目录，再打开根 `README.md`。
2. 用 `Ctrl+Shift+V` 打开内置 Markdown 预览，或用 `Ctrl+K` 然后按 `V` 在右侧预览。
3. 点击表格中的课程或学习目标，再继续打开笔记、代码和报告。课程旧 `readme.md` 顶部也有新的导航入口。

如果使用已安装的 **Markdown Preview Enhanced**，可从命令面板运行它的 **Open Preview to the Side**。保持一个目录入口，再从预览点击相对链接进入正文。PDF 可用已安装的 PDF 预览扩展查看。

想同时保留导航与正文时，把首页预览固定在一侧，另一侧查看笔记与代码；内置预览可用 **Markdown: Toggle Preview Locking** 锁定当前页。以上快捷键、预览和大纲功能见 [VS Code 官方说明](https://code.visualstudio.com/docs/languages/markdown)。

## 找资料与跳转

| 需求 | VS Code 操作 |
|---|---|
| 查某门课程 | 首页 → [课程总览](courses.md) → 课程首页 |
| 考前 10–20 分钟 | [复习入口](../study/revision.md) → 已有快速复习 / 速查 |
| 查某个实验答辩 | [答辩入口](../study/defense.md) → 对应实验的问题与实现 |
| 跨课程查概念 | [知识索引](../knowledge/index.md)，或 `Ctrl+Shift+F` 搜索中文、俄文、英文术语 |
| 按文件名打开 | `Ctrl+P`，输入 `quick-review`、`cheatsheet`、`semester-05` 或课程文件名 |
| 在长笔记中找章节 | `Ctrl+Shift+O`；也可用侧边栏 Outline / 大纲 |

搜索正文时，可在“包含的文件”填 `**/*.md`；查实现则按课程目录搜索 `.java`、`.py`、`.cs` 等。这样不会把第三方依赖文档当成自己的复习资料。

根目录的 [Study-Note.code-workspace](../Study-Note.code-workspace) 可直接用 VS Code 打开。它只为本项目设置 Markdown 自动换行、预览字号与行距，并排除依赖和生成目录的搜索噪声；原有 `.vscode` 的 C++ / Java 配置继续保留。任务菜单内提供导航更新操作，**阅读本身不需要运行任务**。

## GitHub：同一套导航

把改动提交并推送到 GitHub 后，仓库首页会直接显示新的 README。所有相对链接仍然指向原仓库文件，无需 GitHub Pages。按“学期 → 课程 → 复习 / 答辩 / 实验”浏览即可。

[知识图](../knowledge/index.md)使用 GitHub 可直接渲染的 Mermaid 代码块，见 [GitHub 官方说明](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)。公式、表格和代码块也保留在 Markdown 原文中。

## 维护资料

编辑已有笔记可直接保存，不用重新生成入口。新增资料后，在 [catalog.json](catalog.json) 中增加真实文件路径，再运行下面两个轻量脚本；只需 Node.js，不需要安装网站依赖：

```sh
node tools/generate-index.mjs
node tools/update-course-links.mjs
```

完整维护规则见 [维护说明](maintenance.md)。[网站](website.md)是额外阅读方式，可自行从终端运行，不影响 VS Code 与 GitHub 的日常阅读。
