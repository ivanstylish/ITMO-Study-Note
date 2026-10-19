# 代码阅读与排版

Java、测试代码和 static 下的 HTML/CSS/JavaScript 使用 4 个空格缩进，续行也使用 4 个空格，目标行长为 120。长表达式优先拆成局部变量，不用连续的链式调用和参数换行把代码推到屏幕右侧。

例如错误响应先得到 message，再调用 `error(status, message)`；Map.of 中一对键值放在同一行；较长的请求构造与结果读取分步书写。业务规则、接口路径和技术栈保持原样。

每个 Java 文件中，每种注解首次出现处都有中文注释，涵盖 Spring、JPA、Validation、Jackson 和测试注解。同一种注解在同一文件后续出现时不重复解释。static 文件中的关键流程也保留中文注释。

IDEA 会读取项目根目录的 `.editorconfig`。手动查看设置时，Java 的 Indent 和 Continuation indent 均设为 4，关闭多行参数按列对齐。不要再套用此前的 Google Java Format 排版，它可能重新产生多级 8 空格续行。

`.prettierrc.json` 用于静态代码排版。已执行的 Flyway SQL 迁移保持原文，避免单纯格式变化导致历史校验值不匹配。Gradle Wrapper 生成脚本同样保留官方内容。
