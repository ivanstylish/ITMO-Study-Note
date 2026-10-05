# Web Lab4：Spring Boot / React 源码快照

保留 Java 17 / Spring Boot 3.2 后端与 React 19 / Redux Toolkit 前端源码、公开资源和 npm 包锁文件。后端 static 目录中的前端打包产物未导入。

本目录为选择性恢复的源码快照，**未在本次整理中构建、运行或验收**。原课程已有笔记和实现继续保留。

Java 源码中的 SecurityConfig 已保留；原始 application.properties、Compose 和服务器发行包未导入。可参考 [公开 Spring 配置示例](./examples/application.example.properties)，其中 `${DB_*}` 由 Spring 在使用该配置时读取环境变量。

后端声明 Java 17 / Spring Boot 3.2.0，但原 Wrapper 指向 Gradle 9.2.1；[Spring Boot 3.2.0 官方构建要求](https://docs.spring.io/spring-boot/docs/3.2.0/reference/html/getting-started.html#getting-started.system-requirements) 列出的支持范围为 Gradle 7.x（7.5 起）和 8.x。该历史 Wrapper 超出声明的支持范围，需先选定兼容构建工具再测试；本次保留原文件作为来源证据，没有升级应用逻辑。前端保留原包锁文件，不能据此认定 React 19 与旧 react-scripts 5 的全部流程已验证。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
