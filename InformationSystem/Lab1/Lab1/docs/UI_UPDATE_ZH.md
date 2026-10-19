# 界面与注册改版 · 2026-09-18

## 使用方式

在 IDEA 中打开 Lab1，JDK 17，运行 CityApplication；工作目录使用项目根目录。访问 http://localhost:8080。
首次请点击 **Регистрация** 注册，注册成功后返回登录。旧的 student/student2 内存账号不再自动生效；数据库账号 s407959 也不是网页账号。

本地数据库仍为 city_lab1，schema 已由 lab1_5742 原地改名为 **lab1_info**，没有清库重建。
数据库连接密码仍保存在被 Git 忽略的 config/local.properties。

## 这次修改

- 登录页：CITY 艺术大字、十座城市真实照片拼图、登录与注册表单；已去掉宣传语、坐标装饰文字和重复引导。
- 照片保存在项目内，可离线显示；作者、来源与许可证见 PHOTO_CREDITS.md，登录页也可打开照片来源。
- 主页：参考 Harvest 的留白和入口卡片，保留简短标题、四个功能入口及账户操作。
- 删除指定的旧页头、页脚与数据库实现说明文字。
- 统一使用自定义红色错误弹窗，不使用 alert/confirm 或浏览器默认校验提示气泡。
- Birthday 和 EstablishmentDate 改为日期选择器，不设置年龄或年份范围限制；表格、详情、特殊操作结果只展示年月日。
- 实体继续使用实验规定的 ZonedDateTime/LocalDateTime。新选日期补零点，生日补 UTC；未改动的已有日期保留原始时间。
- 字段名称首字母大写，保留原有分页、完全匹配筛选、排序、引用删除保护、乐观锁及自动刷新。
- Java、HTML、CSS、JavaScript、YAML 已统一为易读的多行格式；关键实现加入中文注释。未添加运行时依赖。

## 关键代码阅读顺序

以下 Java 路径位于 src/main/java/edu/lab/city；前端位于 src/main/resources/static。

1. config/SecurityConfig.java：登录页、会话认证、CSRF 保护。
2. web/AuthController.java：登录页面、CSRF 令牌和注册接口。
3. service/AccountService.java：注册事务、BCrypt 哈希和数据库登录。
4. repository/UserRepository.java、domain/AppUser.java：EclipseLink/JPA 持久化。
5. auth.html、auth.css、auth.js：城市拼图、登录和注册交互。
6. index.html、style.css：主页和业务面板。
7. app.js：日期适配、详情渲染、操作表单和自动刷新。
8. ui.js、ui.css：共用的红色错误弹窗和表单校验。

## 数据库迁移

- V1/V2 已执行过，保留原文与校验值，避免重排历史 SQL 导致 Flyway checksum mismatch。
- V3 新增 app_user，存储唯一用户名、密码哈希和注册时间，不生成默认账号。
- V4 重新绑定 schema 名称改变后的函数引用。
- 本机已完成 schema 改名；新版程序正常应用新增迁移。其他旧环境应在备份后迁移 schema，并确保 DB_SCHEMA 与数据库中的名称相符。
- 初次使用全新数据库时，Flyway 自动在 lab1_info 中创建所有对象，无需执行改名。

## 验证

本次在独立数据库执行 2 项单元测试、8 项 PostgreSQL 集成测试，均通过。
浏览器验证包括注册、登录、退出、自定义错误弹窗、十张图片加载、日期选择与显示、CRUD、关联删除保护、跨会话同步、五个特殊操作及手机端无横向溢出。
测试没有把账号或示例城市写入日常使用的 city_lab1。

构建命令：运行 gradlew.bat test bootJar。
账号和业务数据都保存在 PostgreSQL，重启应用不会删除它们。

