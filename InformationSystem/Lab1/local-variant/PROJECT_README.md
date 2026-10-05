# 信息系统实验 1 — 变体 5742

本次改版说明见 [UI_UPDATE_ZH.md](docs/UI_UPDATE_ZH.md)。
字体、前端精简与中英俄切换见 [UI_REFINEMENT_ZH.md](docs/UI_REFINEMENT_ZH.md)。

- [完整实现流程、代码结构与界面设计](docs/IMPLEMENTATION_GUIDE_ZH.md)
- [九道答辩题：中俄双语简版](docs/DEFENSE_QA_ZH_RU.md)
- [服务器启动、端口与浏览器访问](docs/DEPLOYMENT_ZH.md)
- [PUML 在线查看方法](docs/UML_VIEWING_ZH.md)
- [新版界面截图](docs/screenshots/)

完整 Java Web 项目，采用 **Gradle Groovy DSL + Java 17 + Spring MVC + EclipseLink + PostgreSQL**。
本机现已配置 `s407959` 连接本地 `city_lab1`，详见 [本机数据库使用说明](docs/LOCAL_DATABASE_ZH.md)。本地连接文件会覆盖下文的通用默认配置。
这是代码与操作说明，不是实验报告。俄语结论在 docs/CONCLUSION_RU.md。

## 1. 打开项目

1. 在 IntelliJ IDEA 中选择 **File → Open**，打开本项目的 Lab1 文件夹。
2. 选择按 Gradle 项目导入，构建配置是 **build.gradle**，不是 Maven，也不是 Kotlin DSL。
3. 在 Project Structure 中选择 **JDK 17**。
4. 在 Settings → Build, Execution, Deployment → Build Tools → Gradle 中：
   - Gradle distribution 选择 **Wrapper**；
   - Gradle JVM 选择 **JDK 17**；
   - Build and run using 选择 **Gradle**。
5. 等待依赖同步完成。首次使用 Wrapper 需要联网下载 Gradle 8.5 和依赖。项目包含官方 Gradle 生成的 gradlew、gradlew.bat、gradle/wrapper/。
6. 不需要 Lombok、Node.js、前端包管理器、独立 Tomcat 或付费版 IDEA。

Gradle Wrapper 固定构建工具版本。Java 17 与 Gradle 8.5 的兼容性可见 [Gradle 官方兼容表](https://docs.gradle.org/8.5/userguide/compatibility.html)。
若老版 IDEA 对 Gradle 导入提示兼容问题，优先使用下方终端命令构建，并检查 IDE 支持的 Gradle 版本；不要把 Gradle JVM 设为 Java 8/11。

## 2. 准备本地 PostgreSQL

**方案 A：使用已经安装的 PostgreSQL（本机已检测到 PostgreSQL 17）。**

在 pgAdmin 中用管理员账号连接数据库。先连接 postgres 数据库创建登录角色，然后创建数据库；CREATE DATABASE 必须作为单独语句执行，不能放在事务块中：

```sql
CREATE ROLE city_app LOGIN PASSWORD 'city_local_password';
```

```sql
CREATE DATABASE city_lab1 OWNER city_app;
```

也可以在 PowerShell 中运行下面的脚本：先输入 PostgreSQL 管理员的密码，再按提示为新建 city_app 设置密码：

```powershell
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f .\scripts\create-local-db.sql
```

如果角色或数据库已存在，不要重复创建。使用现有数据库时修改 DB_URL、DB_USER、DB_PASSWORD。

**方案 B：已经安装 Docker Desktop 时使用项目附带的 compose.yaml。**

```powershell
docker compose up -d db
```

两种方案二选一；如果已有 PostgreSQL 占用 5432 端口，直接使用方案 A，或者修改 Docker 端口映射并同时修改 DB_URL。数据保存在数据库中；不是 Java 内存集合，也不是 H2。

## 3. 启动

默认配置：

| 配置 | 默认值 |
|---|---|
| DB_URL | jdbc:postgresql://localhost:5432/city_lab1?currentSchema=lab1_info |
| DB_USER | s407959（本机配置） |
| DB_PASSWORD | 本地配置或环境变量提供 |
| DB_SCHEMA | lab1_info |
| SERVER_ADDRESS | 127.0.0.1 |
| PORT | 8080 |

Flyway 会在首次启动时创建 schema、表、约束、触发器和五个数据库函数，以后只运行尚未执行的迁移。DB_SCHEMA 同时配置连接的 schema 和 Flyway，不要求手动执行 V1/V2。

**IDEA 内启动：** 打开 src/main/java/edu/lab/city/CityApplication.java，运行 main 方法。自定义连接时，在 Run/Debug Configuration → Environment variables 中加入上述变量。例如：
`DB_USER=city_app;DB_PASSWORD=自己的密码`。
IDEA 运行配置的环境变量和 PowerShell 的环境变量是两处独立设置。

**或者在项目根目录的 PowerShell 中启动：**

```powershell
.\gradlew.bat bootRun
```

出现 Started CityApplication 后，访问 [http://localhost:8080](http://localhost:8080)。

打开登录页后先点击 **Регистрация** 注册，再用新账号登录。原 student/student2 内存演示账号已移除。

账号保存在 lab1_info.app_user，密码只保存 BCrypt 哈希。网页账号与 PostgreSQL/学校 SSH 账号相互独立。

## 4. 按这个顺序演示实验

1. 登录，进入 **Координаты**，创建坐标，例如 x=0、y=0；再建 x=3、y=4。
2. 进入 **Губернаторы**，创建一个 Human。name 不能为空、age/height 必须 >0。Birthday 可以留空，或通过日期选择器选择年月日，不需要时分秒和时区。
3. 进入 **Города** 创建城市。coordinates 从已存在的坐标中选择；governor 可选择现有 Human，也可为空。id、creationDate 自动生成。
4. 新建两个示例城市：
   - A：area=1，坐标(0,0)，海拔=0，establishmentDate=1900-01-01T00:00；
   - B：area=2，坐标(3,4)，海拔=12，establishmentDate=2000-01-01T00:00。
   - 两者 population 取正整数、standardOfLiving 选 LOW，其余可空字段可留空。
5. 在城市表格中查看 13 个业务属性，各占一列。关联对象列显示 ID 和摘要，**Просмотр** 窗口展示对象及关联对象全部字段。
6. 使用 **Найти по ID** 查看指定对象；分别在独立弹窗中创建、查看、修改和确认删除。表格的 **Изменить** 可直接进入修改。
7. 使用顶部筛选栏。name、governor.name、climate、government、standardOfLiving 支持完全匹配筛选及排序；匹配区分大小写。枚举值按页面列出的英文名称输入。
8. 超过一页后使用分页按钮。城市分页、筛选和排序由服务器完成；关联对象管理页也提供分页显示。
9. 先注册两个账号，分别在普通窗口和无痕窗口登录。任意一端操作后另一端自动更新，通常不超过 2 秒；无需手动刷新。
10. 在两端打开同一个对象进行修改：一端先保存，另一端保存旧版本会返回 409 冲突提示，要求重新打开对象。
11. 尝试删除被城市引用的 Coordinates 或 Human：删除应失败并显示原因。先在城市中改用其他坐标、解除 governor 关联，或删除引用它的城市，再删除辅助对象。
12. 进入 **Специальные операции**，执行全部 5 个操作。上述 A/B 示例结果：平均海拔 6；面积分组各 1；最大→最小城市距离 13；原点→最新成立城市距离 13。

## 5. 特殊操作的明确约定

题目没有定义路线算法和坐标单位。本项目采用三维欧氏直线距离：
`sqrt((x2-x1)^2 + (y2-y1)^2 + (z2-z1)^2)`，z=metersAboveSeaLevel，假定 x/y/z 单位相同。
这不是道路导航距离，也没有把 x/y 当经纬度。若教师要求二维或其他定义，应修改 V2 中对应函数，并为已初始化数据库增加 V3 迁移，不要直接修改已经应用的历史迁移。

| 操作 | PostgreSQL 函数 | 空值与边界 |
|---|---|---|
| 平均海拔 | average_elevation() | 忽略 NULL 海拔；没有已知海拔时返回 NULL |
| 按面积分组计数 | group_by_area() | 使用数据库 real 存储后的精确值分组；空表返回空数组 |
| 名字包含子串 | names_containing(text) | 区分大小写；% 和 _ 是普通字符；空子串匹配全部名字 |
| 最大面积→最小面积 | route_extreme_areas() | 面积并列时选最小 ID；空表 NULL；同一城市距离 0；不同端点缺海拔时报错 |
| 原点→最新成立城市 | route_newest_city() | 按 establishmentDate，而不是 creationDate；忽略未知成立日期；并列最小 ID；无候选 NULL；缺海拔时报错 |

Human.birthday 在 Java 中为 ZonedDateTime，数据库使用 timestamptz。转换器保留时间点，读取统一为 UTC，不保存原来的地区时区名称。
City.creationDate 以 UTC 当前日期自动生成，并由数据库触发器保护，不能修改。
数值 NaN/Infinity、非正面积/人口/年龄/身高、y ≤ -531 均会被拒绝。
持久化实体 ID 使用 Long 包装类型表达保存前的 null，保存后由 PostgreSQL identity 生成正整数；数据库值域仍为题目要求的 64 位整数。
为保护 64 位整数精度，JSON 中 Long/long 序列化为十进制字符串。Java/数据库字段仍为整数，前端输入不会丢失 2^53 以上的数字。

## 6. 项目结构和实现顺序

```text
Lab1/
  build.gradle / settings.gradle      Gradle Groovy DSL
  gradlew / gradlew.bat / gradle/      Gradle Wrapper
  src/main/java/edu/lab/city/
    CityApplication.java              启动入口
    config/                           EclipseLink、事务、认证、JSON
    domain/                           City、Coordinates、Human、枚举、时间转换器
    dto/                              接收请求、返回分页和函数结果
    repository/                       EntityManager 查询及数据库函数调用
    service/                          事务、CRUD、版本检查、特殊操作
    web/                              Spring MVC REST 控制器及错误处理
  src/main/resources/
    application.yml                   通过环境变量配置
    db/migration/                     PostgreSQL 建表与函数
    static/                           浏览器界面，无前端构建依赖
  src/test/java/edu/lab/city/          验证与 PostgreSQL 集成测试
  scripts/                            本地建库和服务器启动脚本
  docs/diagrams/                      UML 图和 draw.io 可编辑文件
  docs/DEPLOYMENT_ZH.md                学校服务器部署步骤
  docs/TESTING_ZH.md                   测试方法与验收清单
  docs/CONCLUSION_RU.md                简短俄语结论
```

阅读或自行重做时的推荐步骤：
1. 根据字段约束建立三个实体与三个枚举，确认关联关系。
2. 编写 PostgreSQL 表、CHECK、NOT NULL、identity、外键及版本变更触发器。
3. 配置 EclipseLink 的 EntityManagerFactory 和 JpaTransactionManager；不引入 Hibernate ORM。
4. 在 repository 层通过 EntityManager 访问数据库，在 service 层包裹事务。
5. 添加 DTO 验证、REST 接口、统一错误响应与版本冲突处理。
6. 完成浏览器菜单、表格、分页、完全匹配筛选和独立弹窗。
7. 编写五个数据库函数，由 SpecialService → SpecialRepository 调用。
8. 用数据库 revision 轮询让所有客户端同步，再执行测试和打包。

EclipseLink 是实际 ORM provider，明确使用 Spring 的 EclipseLinkJpaVendorAdapter 配置；Spring 官方说明了这类 [JPA 集成方式](https://docs.spring.io/spring-framework/reference/data-access/orm/jpa.html)。
依赖里 Hibernate Validator 只用于 Jakarta Bean Validation，不是 Hibernate ORM。五个操作按 PostgreSQL [CREATE FUNCTION](https://www.postgresql.org/docs/current/sql-createfunction.html) 实现。

## 7. UML、测试和打包

- 实体类图：[domain-classes.drawio](docs/diagrams/domain-classes.drawio)，同名 PNG / SVG 可直接查看。
- 应用层类图（含注册认证）：[application-classes.drawio](docs/diagrams/application-classes.drawio)，同名 PNG / SVG 可直接查看。
- 包图：[packages.drawio](docs/diagrams/packages.drawio)，同名 PNG / SVG 可直接查看。
- 可编辑文件通过 draw.io 的“文件 → 从设备打开”加载；具体步骤见 [UML_VIEWING_ZH.md](docs/UML_VIEWING_ZH.md)。三张图均不设置图内标题。

```powershell
.\gradlew.bat clean test bootJar
java -jar .\build\libs\city-lab1.jar
```

生成的 build/libs/city-lab1.jar 包含应用、依赖、静态页面和数据库迁移。服务器运行它只需要 Java 17 与可访问的 PostgreSQL。
完整数据库测试需另外配置临时测试数据库并运行 integrationTest，见 docs/TESTING_ZH.md。
学校服务器部署、SSH 上传及隧道访问的逐步解释见 **docs/DEPLOYMENT_ZH.md**。
