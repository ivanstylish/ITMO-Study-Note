# Web Lab3 / OPI Lab4：历史源码变体

这是与主 Lab3 不同的 JSF / MBean 版本，保留原有相对位置；其 MBean Java 位于 WEB-INF/mbean。它不替代主 Lab3 或 OPI 现有实现。

本目录为选择性恢复的源码快照，**未在本次整理中构建、运行或验收**。原课程已有笔记和实现继续保留。

HttpUnit 工具副本、报告、服务器发行包和数据库配置未导入。Java 源目录与 MBean 编译关系尚未验证。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
