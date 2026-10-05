# 信息系统 Lab1：独立本地源码版本

保留另一份 Spring / EclipseLink 应用源码、原有 docs 与可编辑 UML 图。大量同名 Java / 前端文件与当前 Lab1/Lab1 不同，因此整份独立保存。PROJECT_README.md（若通过检查）为此版本原说明。

本目录为选择性恢复的源码快照，运行与构建说明见下方资料。原课程已有笔记和实现继续保留。

Java 树下 JsonConfig、PersistenceConfig、SecurityConfig 与真实 auth.js / i18n.js、UML 图均已保留；这些源文件中的密码字段/类型和翻译标签不是硬编码连接秘密。原运行 config、application.yml、Compose 和本地数据库创建配置未导入。

构建文件声明 Java 17、Spring Boot 3.3.5、EclipseLink 4.0.4 与 Jakarta Persistence 3.1；Wrapper 指定 Gradle 8.5。可参考 [公开 Spring 配置示例](./examples/application.example.yml)，数据库地址和凭据通过环境变量提供，示例不自动启用。该项目原测试任务把 PostgresIntegrationTest 分开，需要另设一次性测试数据库。

PROJECT_README.md 与 docs 为此版本的原文，部分仍含作者历史磁盘路径或引用未导入的部署资料，请将其当作来源说明。本目录单独保存这一实现版本。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
