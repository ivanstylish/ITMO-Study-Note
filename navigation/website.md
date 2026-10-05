# 网站阅读与全文搜索

[课程总览](./courses.md) · [知识索引](../knowledge/index.md) · [复习](../study/revision.md) · [答辩](../study/defense.md)

网站使用 [VitePress 1.6](https://vuejs.github.io/vitepress/v1/guide/getting-started)、[本地全文搜索](https://vuejs.github.io/vitepress/v1/reference/default-theme-search)与 [Mermaid](https://mermaid.js.org/config/usage.html)。搜索索引随静态站生成，搜索过程无需账号或外部服务；支持中文、俄语与英文关键词。右上角可以切换深浅色。

## 本地运行

先安装 Node.js 20 或以上，在仓库根目录执行：

```sh
npm ci
npm run docs:dev
```

浏览终端显示的本地地址。新增笔记后重新运行 `npm run docs:prepare`，再刷新页面；网站读取的是一次生成的快照。

构建与预览：

```sh
npm run docs:build
npm run docs:preview
```

`.build/site/` 是可托管的静态文件。请使用 HTTP 预览服务器，直接双击 HTML 不能可靠加载站点模块。

## 保持单一内容来源

- 课程笔记、学期入口、知识索引与复习页仍在原仓库路径编辑。
- `tools/build-site.mjs` 只将课程范围内的 Markdown 投影到 `.build/docs/`；生成目录不提交。
- PDF、DOCX、PPT、代码与目录使用 GitHub 原文件链接，不复制进站点。原笔记引用的图片从原仓库读取，首次加载图片需要网络。
- 空文件、依赖、构建产物、维护提示词、部署笔记和检测到的凭据文本不进入网站或搜索索引。具体排除名单写入本地 `.build/site-manifest.json`，其中只记录路径与原因。
- 原笔记中的 HTML 不执行，旧式 MathJax 脚本由构建时公式渲染替代；Vue 模板表达式按文字显示。旧资料的缺图显示提示，缺失链接用点状样式标记，不创建空页面来填补。

构建依赖固定版本并提交锁文件；VitePress 1.6.4 使用兼容的 Vite 6.4.3 覆盖版本，`markdown-it` 与 `xmldom` 固定到修复版本。更新依赖后应重新运行 `npm audit` 和完整构建；开发服务默认只监听本机 `127.0.0.1`。

这只是公开阅读投影，不能代替代码审查或秘密扫描。报告和源代码的 GitHub 链接在本地新增文件提交并推送后才可在线访问。

## GitHub Pages

[官方部署说明](https://vuejs.github.io/vitepress/v1/guide/deploy#github-pages)说明了 Pages 配置。仓库提供 `.github/workflows/knowledge-base.yml`：PR 自动构建，手动运行默认只构建；只有在 Actions 手动勾选 `deploy` 并将仓库 Pages 的 Source 设为 GitHub Actions 后才会发布。

项目站点使用仓库名作为基础路径，本地开发默认 `/`。自定义路径可通过环境变量 `DOCS_BASE` 指定，例如 PowerShell：

```powershell
$env:DOCS_BASE = '/ITMO-Study-Note/'
npm run docs:build
Remove-Item Env:DOCS_BASE
```

网站配置与主题在 `site/.vitepress/`，内容导航由 `navigation/catalog.json` 读取。添加课程或变更学期时先更新课程目录，再运行导航生成器和网站构建。
