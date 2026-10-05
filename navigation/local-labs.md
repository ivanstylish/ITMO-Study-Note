# 补回的本地实验 · Восстановленные исходники

[首页](../README.md) · [实验索引](labs.md) · [维护规则](maintenance.md)

本次从已有本地课程项目中选择性恢复源码和必要的小资源。不同实现保留为独立快照，原仓库实现未覆盖。每个快照的 README 说明依赖、缺失配置和版本差异；`import-manifest.json` 保存文件大小与 SHA256。

| 课程 | 收录入口 | 使用方式 |
|---|---|---|
| Web | [Lab 2：Servlet / JSP](../WebProgramming/Lab2/README.md) | 原 Gradle WAR 项目；核对 JDK 与 Jakarta API 的兼容性 |
| Web | [Lab 3：JSF / JPA / JMX](../WebProgramming/Lab3/local-source/README.md) | 与现有实验要求配合阅读 |
| Web | [Lab 4：Spring Boot / React](../WebProgramming/Lab4/local-source/README.md) | 后端与前端源码；构建输出不归档 |
| Web / 软件工程 | [Lab 3 / OPI Lab 4 变体](../WebProgramming/Lab3/opi-variant/README.md) | JSF / MBean 历史实现，与主版本并存 |
| 编程语言 | [Work 8：反射与动态 IL](../ProgrammingLanguage/work8/README.md) | .NET 8 项目；动态 IL 示例未在 Main 调用 |
| 编程语言 | [早期 C / C++ 变体](../ProgrammingLanguage/local-variants/class01/README.md) · [Class 1](../ProgrammingLanguage/local-variants/class1/README.md) · [Class 2](../ProgrammingLanguage/local-variants/class2/README.md) | 保存仓库此前没有的源码；部分是片段 |
| 编程语言 | [Class 3：战斗程序](../ProgrammingLanguage/local-variants/class3/README.md) · [Class 5：服务片段](../ProgrammingLanguage/local-variants/class5/README.md) · [Native C](../ProgrammingLanguage/local-variants/fast_lib/README.md) | 不覆盖 work 1–7；接口需参考原项目 |
| 计算数学 | [Lab 1：简单迭代法变体](../ComputationalMath/Lab1/local-variant/README.md) | 与原 src 对照，保留变体 15 与 test 1–6 |
| 算法 | [Part 9–16](../AADS/local-lab1/README.md) | 各自有 main，分别编译 |
| 信息系统 | [Lab 1：独立本地版本](../InformationSystem/Lab1/local-variant/README.md) | 与已收录 Spring / EclipseLink 项目分开保存 |

没有导入上游 Wrench 工具、WildFly 发行包、IDE 缓存、依赖、编译文件、重复大数据或原始私人连接配置。保留的项目需要按各自 README 配置环境；大一、大二课程与实验的状态已统一更新为 ✓ 已通过。

```sh
# 不需要访问原电脑即可核验当前快照
node tools/import-local-labs.mjs --verify

# 后续导入先预览；路径指向包含课程目录的本地父目录
node tools/import-local-labs.mjs --source-root <course-projects-directory>
# 审阅预览后复制，不覆盖内容不同的既有文件
node tools/import-local-labs.mjs --source-root <course-projects-directory> --apply
```

本地盘保持原样；恢复工具仅扫描明确列出的课程目录，不执行源码或读取整个磁盘。
