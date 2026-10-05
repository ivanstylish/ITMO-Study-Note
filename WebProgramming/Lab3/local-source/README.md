# Web Lab3：JSF / JPA / JMX 源码快照

保留 JSF / PrimeFaces 页面、PointBean / ResultBean、EclipseLink 实体、区域判断测试和 JMX MBean。现有 Lab3 学习笔记继续作为课程入口。

本目录为选择性恢复的源码快照，**未在本次整理中构建、运行或验收**。原课程已有笔记和实现继续保留。

代码使用 `jakarta.*` 与 `@Serial`；依赖声明 Servlet 5、Faces 3、Persistence 3 和 EclipseLink 3.0.3。Wrapper 文件指定 Gradle 8.2，但 build.gradle 中 wrapper 任务配置写 7.6，两个来源尚未协调；可先采用 JDK 17 检查此历史工程。应用服务器版本的运行兼容性没有验证。

原始数据库连接、persistence.xml、build.properties 和应用服务器未导入。可参考 [公开持久化模板](./examples/persistence.example.xml)，单位名称 `CoordinatePU` 来自实际 ResultBean。JPA 不会自动把这个 XML 的 `${DB_*}` 字符串替换为环境变量；必须先在本地安全展开模板并生成私有配置，或改用服务器数据源，再验证部署。不要直接复制模板后声称已经连接数据库。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
