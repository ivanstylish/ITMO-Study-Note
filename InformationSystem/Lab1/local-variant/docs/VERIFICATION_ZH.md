# 本次交付的验证记录

验证环境：Windows、Amazon Corretto Java 17.0.11、Gradle 8.5、PostgreSQL 17、Chrome 152。

- `test`：2 项单元测试通过。
- `integrationTest`：5 项真实 PostgreSQL 集成测试通过。
- `bootJar`：成功生成 `build/libs/city-lab1.jar`。
- 使用生成的 JAR 实际启动应用，独立 schema `s5742_browser` 自动初始化成功，验证 DB_SCHEMA 可配置。
- 真实浏览器中使用两个独立登录会话，完成关联对象创建、城市创建/查看/修改、引用删除保护及跨会话自动刷新。
- 真实浏览器中执行全部五个特殊操作，验证路线样例返回 13。
- 创建 12 个城市后验证分页（10+2）和 name 完全匹配筛选，`Page 1` 不匹配 `Page 10`。
- 验证人口 `9007199254740993` 在数据库、API 和网页之间保持完整精度。
- 浏览器运行期间未检测到未捕获 JavaScript 异常。
- 类图与包图已改为 draw.io 可编辑文件，并提供 PNG / SVG。已在本地检查 XML 结构、连接引用和图片排版。

学校服务器部署尚未实际执行：未提供学校 SSH 主机、端口及账户凭据。部署说明按题目明确给出的 PostgreSQL 主机 `pg`、数据库 `studs` 编写，未知的 SSH 参数保留为占位符。

测试使用独立临时 PostgreSQL 实例和测试数据库，没有连接或修改用户已有的 PostgreSQL 业务数据。
