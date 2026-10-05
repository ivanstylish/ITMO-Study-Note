# Web Lab2：Servlet / JSP 源码

保留 Servlet 控制器、区域判断与 HitResult 模型、JSP、浏览器 JS/CSS 和 Gradle WAR 工程。构建描述声明 Java 11、Jakarta Servlet 6.0 / JSP 3.1。

本目录为选择性恢复的源码快照，**未在本次整理中构建、运行或验收**。原课程已有笔记和实现继续保留。

构建描述设置 Java 11、Jakarta Servlet 6.0 / JSP 3.1，当前 Wrapper 文件指定 Gradle 8.2。需要相应 JDK 与 Jakarta Servlet 服务器；它不是使用 `javax.servlet` 的旧 Java EE 项目。服务器发行包和字体未导入，实际服务器/JDK 组合尚未测试。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
