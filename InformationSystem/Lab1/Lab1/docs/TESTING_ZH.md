# 测试与验收

## 自动测试命令

无需数据库的测试：

```powershell
.\gradlew.bat test
```

覆盖 ORM 层字段边界、NaN/Infinity 和 ZonedDateTime 转换。

集成测试使用真实 PostgreSQL、Spring MVC MockMvc、EclipseLink、事务与 Flyway，不使用 H2。
必须先准备**可清空的专用测试数据库**，例如 city_lab1_test。测试会 TRUNCATE 实验的三个业务表，不可指向正式数据、学校 studs 或你的日常实验数据库。

```powershell
$env:TEST_DB_URL='jdbc:postgresql://localhost:5432/city_lab1_test'
$env:TEST_DB_USER='city_app'
$env:TEST_DB_PASSWORD='city_local_password'
.\gradlew.bat integrationTest
```

若测试环境继承了 DB_SCHEMA，请移除该环境变量，或设回 lab1_info，因为测试中的直接 SQL 使用 lab1_info。

自动测试覆盖：
- 未登录请求被拒绝、修改请求必须携带 CSRF；
- 城市 CRUD、现有关联对象选择、关联对象详细信息；
- 两个已认证用户对同一数据库的可见性和 revision 更新；
- 引用中的 Human/Coordinates 删除失败，解除引用后可以删除；
- 过期版本修改被拒绝；
- 所有五个数据库函数，包括 NULL、空表、相同起终点；
- 子串搜索中 %/_ 按普通字符处理；
- 完全匹配筛选、分页、排序字段白名单；
- 数据库直接写入绕过 HTTP 时的 CHECK 约束；
- 超过 JavaScript 安全整数范围的 Long 往返不丢精度；
- creationDate 不可被 SQL 更新。

测试报告由 Gradle 生成在 build/reports/tests/test/ 和 build/reports/tests/integrationTest/。

## 浏览器验收

1. 先注册两个新账号，在两个不同浏览器会话分别登录。
2. 新增/修改/删除城市，另一端无需点击刷新，应在约 2 秒内更新。
3. 在两端同时打开编辑窗口，验证第二次提交旧版本不会覆盖第一次。
4. 添加 11 个以上城市，确认默认每页 10 个，分页后排序和筛选仍有效。
5. 查询 ID，确认返回完整关联对象属性。
6. 检查每个输入的必填、数值范围和空值提示。
7. 关闭网络或暂停服务器，页面提示连接错误；恢复后轮询自动重试。
8. 修改关联对象时，所有引用它的城市显示新的摘要。
9. 进入特殊操作页执行操作，再在另一端修改数据，结果区自动重新查询。

关于删除要求：City 引用 Coordinates/Human，外键方向是 City → 辅助对象。
不能删除被城市引用的辅助对象；可以删除城市本身，且不会级联删除共享坐标或人。
题目未提供其他指向 City 的业务对象，因此不人为增加反向依赖来阻止正常的城市删除。

