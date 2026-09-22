# 实验一答辩：中俄双语答案

适用项目：City Registry，变体 5742。每题先理解中文，再用对应俄语回答；项目实例均以本项目实际代码为准。

## 课件与版本说明 / Материалы и версии

- **课件 A**：`D:/Study-Note/InformationSystem/Lecture/is1-javaee.pdf`，48 页。
- **课件 B**：`D:/Study-Note/InformationSystem/Lecture/is2-persistence.pdf`，69 页。
- **课件 C**：`D:/Study-Note/InformationSystem/Lecture/is3-spring.pdf`，89 页。
- 页码指 PDF 阅读器从 1 开始的文件页码，不是幻灯片标题中的章节编号。
- 课件 A 使用较早的 Java EE 术语和 `javax.*` 示例。本项目使用 Java 17、Spring Boot 3.3.5、Jakarta Persistence 3.1、EclipseLink 4.0.4，因此持久化导入为 `jakarta.persistence.*`。Java SE 中的 `javax.sql.DataSource` 不需要改成 `jakarta.sql`。
- 课件 B 的 Jakarta Data 代码用于说明思想，包含命名不一致；不宜直接复制编译。以下答案区分标准、实现和本项目实际使用的功能。

**Русский:** Номера страниц относятся к PDF-файлам. В первой презентации встречаются исторические примеры Java EE и `javax.*`. В проекте используются Jakarta Persistence 3.1 и EclipseLink 4.0.4. Примеры из лекций нужно соотносить с версией API; пакет Java SE `javax.sql` не переименован.

## 1. Шаблоны проектирования и архитектурные шаблоны

### 中文答案

**设计模式**是对反复出现的对象协作问题的可复用解决思路，不是可以直接粘贴的完整代码。常分为创建型（Factory、Builder、Singleton）、结构型（Adapter、Proxy、Decorator）、行为型（Strategy、Observer）。

**架构模式**决定整个系统的主要部分及其职责与依赖，如分层架构、MVC、客户端—服务器、事件驱动。设计模式通常作用于类和对象，架构模式作用于更大范围；两者可以同时使用。

本项目采用分层单体：浏览器 → Controller → Service → Repository → 数据库。Controller 处理 HTTP 和输入，Service 组织业务规则与事务，Repository 封装数据访问。MVC 中，Model 是业务数据和业务逻辑，View 是 HTML/CSS/JavaScript，Controller 是 Spring MVC 控制器；返回 JSON 仍然使用 Spring MVC，请求不一定必须返回服务端模板。

实际例子：`ObjectRepository` 承担 DAO/Repository 职责，隔离 JPA 访问；`Requests` 中的 DTO 描述输入边界；Spring 为 `@Transactional` 服务建立代理，在业务调用前后开始、提交或回滚事务。IoC/DI 是对象创建与依赖管理的原则，不应只背成某一个 GoF 模式。

### Русский ответ

**Шаблон проектирования** — типовое решение повторяющейся задачи взаимодействия классов и объектов. Выделяют порождающие шаблоны, например Factory и Builder, структурные — Adapter и Proxy, и поведенческие — Strategy и Observer.

**Архитектурный шаблон** определяет крупные части системы, их обязанности и связи. Примеры: слоистая архитектура, MVC и клиент-серверная архитектура. Различие прежде всего в масштабе решения.

Моё приложение является слоистым монолитом: контроллер принимает HTTP-запрос, сервис выполняет бизнес-операцию, репозиторий обращается к базе. Представление реализовано на HTML, CSS и JavaScript, а Spring MVC возвращает JSON. Репозитории выполняют роль DAO, DTO задают формат входных данных. Транзакции реализуются через прокси Spring: он открывает и завершает транзакцию вокруг вызова сервиса.

### 常见追问 / Дополнительный вопрос

**为什么不让 Controller 直接写 SQL？** 会把协议、业务和存储逻辑混在一起，不利于测试和复用。分层不等于必须为每个类创建接口，本实验不需要额外复杂化。

**Почему SQL не находится в контроллере?** Иначе смешиваются обработка HTTP, бизнес-правила и хранение данных. Разделение обязанностей упрощает тестирование и изменение приложения; отдельный интерфейс для каждого класса при этом не обязателен.

课件依据：A 第 13、17 页（应用分层），第 21 页（代理）；B 第 61–63 页（DAO）；C 第 32–40 页（MVC），第 77–89 页（AOP）。

## 2. Платформа Jakarta EE. Виды компонентов

### 中文答案

Jakarta EE 是构建企业 Java 应用的一组标准规范，建立在 Java SE 上，继承 Java EE。它规定 API 与行为；兼容的运行时或服务器提供实现。不是一个单独的 JAR，也不是 Java SE 的替代品。

应用组件由容器提供生命周期、依赖注入、安全、事务等基础服务。主要组件包括：Web 组件 Servlet、页面组件；CDI 业务 Bean；Enterprise Beans（EJB）；消息驱动组件；REST 资源。JPA Entity 是持久化对象，不等于 EJB，也不能把所有实体都当作 CDI 服务 Bean。

EJB 中，Stateless 不保存客户端跨调用会话状态；Stateful 保存特定客户端的会话状态；Singleton 提供共享单例组件；Message-Driven Bean 异步接收消息。Servlet 容器和完整 Jakarta EE 服务器的能力不同，普通 Tomcat 不自动提供完整 EJB/CDI/JPA 平台。

课件讨论 Full/Web Profile；较新的平台还有 Core Profile，应按课程版本说明。位置透明是某些远程组件机制提供的能力，单有 CDI 注入并不会把任意本地方法自动变成远程调用。

### Русский ответ

Jakarta EE — набор спецификаций для корпоративных Java-приложений, основанный на Java SE и являющийся продолжением Java EE. Спецификации определяют API и поведение, а совместимый сервер предоставляет реализации.

Компоненты работают под управлением контейнера, который обеспечивает жизненный цикл, внедрение зависимостей, безопасность и транзакции. К компонентам относятся Servlet, CDI-бины, Enterprise Beans, обработчики сообщений и REST-ресурсы. JPA Entity представляет сохраняемые данные и не является EJB.

Session Beans бывают Stateless, Stateful и Singleton. Stateless не хранит состояние сеанса конкретного клиента между вызовами; Stateful хранит; Singleton предоставляет общий экземпляр компонента. Message-Driven Bean обрабатывает сообщения асинхронно. Servlet-контейнер не равнозначен серверу полного профиля Jakarta EE.

### 本项目 / В проекте

使用 Spring 管理服务，嵌入式 Tomcat 处理 Servlet 请求，EclipseLink 提供 JPA。没有实现 EJB、JMS、远程 RMI，也没有声称部署了完整 Jakarta EE 平台。

**Русский:** Сервисы управляются Spring, HTTP обрабатывает встроенный Tomcat, а JPA реализует EclipseLink. EJB, JMS и RMI в проекте не используются.

课件依据：A 第 3–4、13–17、19–25、28、31、43–44 页。版本补充：[Jakarta EE 规范目录](https://jakarta.ee/specifications/)。

## 3. Jakarta EE. Управляемые бины. CDI-бины

### 中文答案

Managed Bean 泛指由容器管理生命周期的对象：容器创建它、注入依赖、调用初始化与销毁回调。普通 `new` 出来的对象不会自动获得所有容器服务。

CDI 是 Contexts and Dependency Injection，提供类型安全依赖注入与上下文生命周期管理。`@Inject` 声明注入点；Qualifier 在同一类型有多个实现时区分候选者；作用域决定实例存活范围，例如 `@RequestScoped`、`@SessionScoped`、`@ApplicationScoped`、`@Dependent`。`@Named` 主要用于给 Bean 提供可由表达式语言使用的名称，不是所有 CDI Bean 的必需注解。

常见生命周期：构造 → 注入 → `@PostConstruct` → 使用 → `@PreDestroy`。Producer 可以把工厂方法的产物交给容器。会话等可钝化作用域还需要满足相应序列化和依赖要求。

课件 A 第 5 页使用旧 JSF `@ManagedBean/@ManagedProperty`；这是历史 JSF 管理 Bean 示例，不能当成现代 CDI 的标准写法。CDI 的注入通常写 `@Inject`，旧 JSF Bean、CDI Bean、Spring Bean 应分别辨认。

### Русский ответ

Управляемый бин — объект, жизненным циклом которого управляет контейнер. Контейнер создаёт экземпляр, внедряет зависимости и вызывает методы жизненного цикла.

CDI означает Contexts and Dependency Injection. Он обеспечивает типобезопасное внедрение зависимостей и управление контекстами. `@Inject` обозначает точку внедрения, квалификаторы выбирают нужную реализацию, а область видимости определяет время жизни экземпляра: запрос, HTTP-сеанс, приложение или зависимый объект. `@Named` задаёт имя, например для обращения из EL, но требуется не каждому CDI-бину.

Обычная последовательность: создание, внедрение зависимостей, `@PostConstruct`, использование и `@PreDestroy`. Исторические JSF-аннотации `@ManagedBean` и `@ManagedProperty` из лекции следует отличать от современного CDI.

### 本项目 / В проекте

`@Service`、`@Repository`、`@Configuration` 注册的是 Spring Bean，由 Spring ApplicationContext 管理。它们实现类似的 DI 思想，但本项目没有启用 CDI 容器。`City` 是 JPA Entity，受持久化上下文管理，而不是全局单例服务。Spring 默认 singleton 是每个容器、每个 Bean 定义一个实例，不等于整个 JVM 永远只有一个实例，也不自动保证线程安全。

**Русский:** В проекте используются Spring-бины, а не CDI-бины. `City` управляется контекстом персистентности как Entity. Область singleton в Spring относится к определению бина внутри контейнера и сама по себе не гарантирует потокобезопасность.

课件依据：A 第 3–5、37–38 页。术语核对：[CDI 4.0](https://jakarta.ee/specifications/cdi/4.0/jakarta-cdi-spec-4.0.html)。

## 4. Концепция ORM. Hibernate и EclipseLink: особенности, API, сходства и отличия

### 中文答案

ORM 是对象—关系映射：类映射表，对象映射记录，属性映射列，对象关联映射外键或关联表。它减少重复 JDBC 代码，但不能消除数据库设计、SQL 与事务知识。

对象模型与关系模型存在阻抗不匹配：对象身份与主键、继承与表、引用与外键、对象图与连接查询。常见继承映射为 SINGLE_TABLE、JOINED、TABLE_PER_CLASS；分别在连接成本、空列、约束和多态查询成本之间取舍，不能说某一种对所有查询都最快。

Hibernate 与 EclipseLink 都是 ORM 框架，也都可以作为 Jakarta Persistence provider。采用标准 JPA API 时，可使用 `EntityManager`、JPQL 和 Criteria API；原生 SQL 也可用于数据库特定操作。

| 对比 / Сравнение | Hibernate | EclipseLink |
|---|---|---|
| 原生入口 / Собственный API | Session、SessionFactory、HQL | EclipseLink Session、扩展查询与配置 |
| 来源 / Происхождение | Hibernate/Red Hat 生态 | Eclipse Foundation，源于 TopLink |
| 标准 / Стандарт | 实现 JPA，另有扩展 / JPA и расширения | 实现 JPA，另有扩展 / JPA и расширения |
| 优化手段 / Оптимизация | 代理、字节码增强、缓存 / Прокси, enhancement, кеш | Weaving、缓存、批量读取 / Weaving, кеш, batch reading |
| 选择依据 / Выбор | 版本兼容、生态、团队与实测 / Совместимость и измерения | 版本兼容、课程要求与实测 / Совместимость и требования |

### Русский ответ

ORM — объектно-реляционное отображение: классы сопоставляются таблицам, объекты — строкам, поля — столбцам, а связи — внешним ключам. ORM уменьшает объём повторяющегося JDBC-кода, но не отменяет необходимость понимать SQL и транзакции.

Основная трудность — различие объектной и реляционной моделей: идентичность, наследование и связи. Для наследования применяют SINGLE_TABLE, JOINED и TABLE_PER_CLASS, выбирая компромисс между структурой таблиц и стоимостью запросов.

Hibernate и EclipseLink реализуют JPA. Общий переносимый API — `EntityManager`, JPQL и Criteria API. Hibernate также предоставляет `Session`, `SessionFactory` и HQL. EclipseLink имеет собственные API и настройки, включая weaving и кеширование. Выбор зависит от требований и совместимости; универсально более быстрого провайдера нет.

### 本项目 / В проекте

通过 `EclipseLinkJpaVendorAdapter` 明确选择 EclipseLink；关闭 weaving 和共享二级缓存，减少启动配置与跨会话陈旧数据问题。一级持久化上下文仍然存在。依赖中的 Hibernate Validator 是 Bean Validation 的实现，**不是 Hibernate ORM**，不代表更换了 ORM。切换 provider 不仅改依赖，还需检查专用设置、SQL 行为和集成测试。

**Русский:** Я явно настраиваю EclipseLink. Weaving и общий кеш второго уровня отключены. Hibernate Validator проверяет ограничения данных и не является Hibernate ORM. Замена провайдера требует проверки конфигурации и поведения запросов.

课件依据：B 第 3–17 页。补充：[Hibernate API](https://docs.hibernate.org/orm/6.6/introduction/html_single/)、[EclipseLink 4.0](https://eclipse.dev/eclipselink/documentation/4.0/)。

## 5. Jakarta Persistence: особенности, API, интеграция с ORM-провайдерами

### 中文答案

Jakarta Persistence（JPA）是持久化标准，不是具体数据库或 ORM 实现。规范定义实体映射、实体生命周期、持久化上下文、查询以及事务相关行为；运行时需要 EclipseLink 或 Hibernate 等 provider 执行这些操作。

Entity 使用 `@Entity`、`@Id`，通过 `@Table/@Column` 描述映射；`@GeneratedValue` 配置主键生成；`@ManyToOne/@JoinColumn` 描述关联；`@Enumerated(STRING)` 用名称保存枚举；`@Version` 用于乐观锁。按本项目 JPA 3.1 的要求，实体需要 public/protected 无参构造函数，不能是 final 类。

`EntityManagerFactory` 是创建 EntityManager 的重量级工厂；`EntityManager` 提供操作并关联 Persistence Context。上下文跟踪托管实体，在同一上下文中，同一实体类型与主键对应一个托管实例。实际 EntityManager 不是可随意在线程间共享的线程安全对象；Spring 注入的代理会委派到当前事务资源。

| API | 中文含义 | Русский |
|---|---|---|
| persist | 让新对象进入托管状态，安排插入 | Сделать новый объект управляемым, запланировать INSERT |
| find | 按主键取得实体，找不到返回 null | Найти по ключу, иначе null |
| merge | 把状态复制到托管实例并返回它，原对象不因此自动托管 | Скопировать состояние в управляемый экземпляр и вернуть его |
| remove | 标记删除托管实体 | Пометить управляемый объект для удаления |
| flush | 将变更同步到数据库，不等于提交 | Синхронизировать изменения, но не завершить транзакцию |
| refresh | 用数据库状态覆盖托管对象当前状态 | Обновить объект из БД |
| detach / clear | 脱离一个 / 全部托管实体 | Отсоединить один объект / очистить контекст |

实体有 New、Managed、Detached、Removed 四种状态。托管实体字段修改可由 dirty checking 在 flush 时写入，无需每次显式调用 update。JPQL 面向实体和属性，SQL 面向表和列；Criteria 用对象构造查询。`LAZY` 表示延迟获取策略，规范中通常是提示；`EAGER` 要求及时加载，但不保证只执行一条 JOIN SQL。

### Русский ответ

Jakarta Persistence — спецификация, а EclipseLink и Hibernate — её реализации. JPA определяет отображение Entity на таблицы, жизненный цикл сущностей, контекст персистентности и API запросов.

`EntityManagerFactory` создаёт EntityManager. EntityManager управляет сущностями в Persistence Context. Состояния сущности: новая, управляемая, отсоединённая и удаляемая. `persist` делает новый объект управляемым, `find` ищет по ключу, `remove` планирует удаление. `merge` возвращает управляемую копию состояния, а исходный объект не обязательно становится управляемым. `flush` отправляет изменения в БД, но не равен commit.

Изменения управляемых объектов отслеживаются автоматически. JPQL обращается к сущностям и их свойствам, native SQL — к таблицам. Стандартный API реализуется провайдером, который формирует SQL и использует JDBC.

### 本项目 / В проекте

`PersistenceConfig` 以 Java 配置创建 EMF，不必同时维护 `persistence.xml`；`@PersistenceContext` 注入 EntityManager；`JpaTransactionManager` 配合 Spring `@Transactional`。`CityService` 在事务中查出实体、校验版本、修改字段，再 flush；`SpecialRepository` 使用 native SQL 调用 PostgreSQL 函数。只有一个数据库，不需要为了实验引入分布式 JTA。

**Русский:** В проекте фабрика настроена Java-конфигурацией. EntityManager внедряется через `@PersistenceContext`, а транзакции обслуживает `JpaTransactionManager`. Обычные операции используют JPA, специальные — native-запросы к функциям PostgreSQL.

课件依据：B 第 19–60 页，重点 39–50、54–60 页。细节核对：[Jakarta Persistence 3.1](https://jakarta.ee/specifications/persistence/3.1/jakarta-persistence-spec-3.1.html)。

## 6. Технология Jakarta Data

### 中文答案

Jakarta Data 是声明式数据仓库访问的标准，目标是减少手写 DAO 的重复代码。开发者声明 Repository 接口、实体类型和操作，provider 提供实现。标准关注 Repository 抽象、查询、分页与排序，可面向不同存储技术；具体存储能力取决于 provider。

它与 JPA 处于不同抽象层：JPA 详细管理关系映射、实体生命周期与持久化上下文；Jakarta Data 提供更高层数据访问接口，可以由 JPA 支撑，但不要求所有实现都等同于关系 ORM。声明接口仍需要 provider 和数据库配置，并不是只写注解就不需要实现依赖。

课件中的 `BasicRepository` 表达通用仓库操作。学习时还需区分 Jakarta Data 的 `jakarta.data.repository.Repository` 与 Spring 的 `org.springframework.stereotype.Repository`：名字类似，含义和包不同。在 Jakarta Data 1.0 中，按方法名推导查询属于规范扩展，不能假定任何 provider 都支持任意 `findBy...` 组合。[Jakarta Data 1.0 规范](https://jakarta.ee/specifications/data/1.0/jakarta-data-1.0)

### Русский ответ

Jakarta Data — стандарт декларативного доступа к данным через репозитории. Разработчик объявляет интерфейс и операции, а провайдер создаёт реализацию. Это уменьшает повторяющийся код DAO и предоставляет абстракции запросов, сортировки и разбиения на страницы.

Jakarta Data и JPA находятся на разных уровнях. JPA описывает объектно-реляционное отображение и жизненный цикл Entity. Jakarta Data описывает более высокоуровневый доступ через Repository и может использовать JPA, но не ограничивается одной технологией хранения.

Нужен совместимый провайдер; одних аннотаций недостаточно. Аннотацию Jakarta Data `Repository` нельзя путать со Spring `@Repository`. Возможности вывода запроса из имени метода следует проверять для выбранной версии и провайдера.

### 本项目 / В проекте

本项目**没有使用 Jakarta Data**。Repository 是手写 Java 类，直接调用 EntityManager。选择它是为了清晰展示实验要求的 JPA 操作，不应在答辩中声称系统自动生成了 Repository 实现。

**Русский:** Jakarta Data в моей работе не используется. Репозитории написаны вручную и вызывают EntityManager, чтобы явно показать работу JPA.

课件依据：B 第 64–69 页。

## 7. Платформа Spring. Сходства и отличия с Java EE

### 中文答案

Spring Framework 是模块化应用框架，核心是 IoC 容器和 DI，提供 AOP、事务抽象、MVC、数据访问集成等能力。开发者通过组件注解、Java 配置或 XML 注册 Bean，容器组装对象。

与 Java/Jakarta EE 的共同点是组件化、DI、生命周期、声明式事务和 Web/数据访问能力。区别在于 Jakarta EE 是多实现的规范集合；Spring 是具体框架与生态，有自己的容器、配置和扩展机制。Jakarta EE 通常由兼容运行时实现平台规范，Spring 可组合所需库并嵌入 Web 容器，也可部署到外部容器。

两者不是互斥关系：Spring 使用 Jakarta Servlet、Persistence、Validation 等 API。Spring `@Service` 和 CDI 作用域注解不能不加分析地互换。`@Transactional` 还需要检查导入包与实际事务管理器。

### Русский ответ

Spring Framework — модульный фреймворк с IoC-контейнером, внедрением зависимостей, AOP, транзакциями, MVC и интеграцией с технологиями доступа к данным.

Общее с Jakarta EE — компонентный подход, управление жизненным циклом, DI и декларативные сервисы. Главное различие: Jakarta EE является набором спецификаций с несколькими реализациями, а Spring — конкретным фреймворком и экосистемой со своим контейнером.

Они могут использоваться совместно: Spring интегрируется с Servlet, JPA и Bean Validation. В моей работе Spring управляет контроллерами, сервисами и репозиториями, а стандарт JPA реализует EclipseLink.

### 常见追问 / Дополнительный вопрос

**为什么 `@Transactional` 可能不生效？** 默认代理模式下，同一个对象内部 `this.method()` 不经过代理；手工 new 的服务也不是容器代理。默认对 RuntimeException/Error 回滚，受检异常需按业务配置 rollbackFor，不能认为任何异常必然回滚。

**Почему транзакция может не открыться?** При стандартном прокси-подходе внутренний вызов `this.method()` не проходит через прокси. Объект, созданный вручную, также не получает автоматически транзакционный перехват. Правила отката зависят от конфигурации и типа исключения.

课件依据：C 第 2–3 页（Spring 与 Java EE），第 8–24 页（容器、Bean、DI），第 25–29 页（配置），第 32–43 页（MVC）；A 第 3–4 页可对照 IoC。补充：[Spring 概览](https://docs.spring.io/spring-framework/reference/overview.html)、[Spring/JPA 集成](https://docs.spring.io/spring-framework/reference/6.2/data-access/orm/jpa.html)。

### 课件补充：ApplicationContext 与 MVC / Дополнение по лекции

ApplicationContext 在 BeanFactory 的对象管理能力上提供更完整的应用上下文，包括事件、资源和国际化等。构造器注入让必需依赖明确，单构造器通常不必写 `@Autowired`；同类型候选者可通过 `@Qualifier` 或 `@Primary` 选择。请求经过 DispatcherServlet、HandlerMapping 和 HandlerAdapter 到达控制器；本项目 `@RestController` 通过消息转换器返回 JSON，不走模板 ViewResolver。

**Русский:** ApplicationContext расширяет возможности BeanFactory, добавляя инфраструктуру событий, ресурсов и интернационализации. Конструктор явно задаёт обязательные зависимости; при единственном конструкторе `@Autowired` обычно не требуется. `@Qualifier` и `@Primary` помогают выбрать бин. DispatcherServlet направляет запрос через HandlerMapping и HandlerAdapter контроллеру. В моём REST API результат преобразуется в JSON, а шаблонное представление не используется.

## 8. Spring Boot

### 中文答案

Spring Boot 基于 Spring，减少启动项目与配置的工作量。主要机制是 starter 依赖组合、自动配置、外部配置、可执行 JAR 与嵌入式服务器。`@SpringBootApplication` 组合应用配置、自动配置和组件扫描。

自动配置依据 classpath、配置属性和已有 Bean 等条件工作，不是无条件替开发者配置所有东西。自定义 Bean 可以替代相应自动配置的默认方案。本项目利用 Boot 启动 Web 与数据源等基础设施，再手动配置 EclipseLink。

Boot 不是 ORM，不等于 Spring MVC，也不等于完整 Jakarta EE 服务器。Spring MVC 负责 Web 请求，EclipseLink 负责 ORM，Boot 负责方便地组装启动。starter 管理依赖组合，不应理解为所有组件版本永远相同或无需兼容性检查。

### Русский ответ

Spring Boot упрощает создание и запуск Spring-приложений. Он предоставляет starter-зависимости, условную автоконфигурацию, внешние настройки и упаковку приложения в исполняемый JAR со встроенным сервером.

`@SpringBootApplication` объединяет конфигурацию приложения, автоконфигурацию и сканирование компонентов. Автоконфигурация зависит от библиотек, свойств и уже объявленных бинов. При необходимости разработчик задаёт собственную конфигурацию.

В проекте Boot запускает приложение и встроенный Tomcat, Spring MVC обрабатывает запросы, а EclipseLink выполняет ORM. Boot сам не является ORM или сервером полного профиля Jakarta EE. Приложение запускается командой `java -jar city-lab1.jar`.

### 本项目 / В проекте

入口 `CityApplication`；`application.yml` 管理端口、数据源、schema、Flyway；本地私密配置通过 `config/local.properties` 导入；`bootJar` 生成可执行 JAR。不需要把静态前端单独部署到 Node 服务。

**Русский:** Точка входа — `CityApplication`, настройки находятся в `application.yml`, а локальные секреты — в исключённом из Git файле. Задача `bootJar` собирает сервер и статические страницы в один артефакт.

课件依据：C 第 55–64 页，重点第 57–60 页（Boot、starter、Gradle、入口），第 62–64 页（外部配置）。课件第 59 页展示 Gradle，说明本实验使用 Gradle Groovy 构建与课程知识相符；本项目保留现有 Boot 3.3.5，不照搬示例中的 Boot 2.7.8。补充：[Boot 3.3 自动配置](https://docs.spring.io/spring-boot/3.3/reference/using/auto-configuration.html)。

## 9. Spring Data

### 中文答案

Spring Data 是 Spring 生态中的数据访问项目家族，包括 JPA、JDBC、MongoDB 等不同模块；不能把整个 Spring Data 都叫作 ORM。

Spring Data JPA 在 JPA 之上提供 Repository 抽象。开发者可以声明继承 `JpaRepository<Entity, ID>` 的接口，由框架创建实现代理，提供 CRUD、分页、排序，并支持方法名派生查询、`@Query` 和自定义实现。具体持久化仍由 JPA provider 完成。

例如教学示意 `interface CityRepository extends JpaRepository<City, Long>`，可声明 `findByName(String name)`；这只是解释 Spring Data 的例子，**不是本项目代码**。复杂查询、事务边界、性能和关联抓取仍需要开发者设计，不能因为自动生成方法就忽略 SQL。

与 Jakarta Data 相比，Spring Data 属于 Spring 生态，Jakarta Data 是 Jakarta 标准；两者理念相近但注解、接口、支持范围和运行时不同，不可直接互换。

### Русский ответ

Spring Data — семейство проектов для доступа к разным хранилищам: JPA, JDBC, MongoDB и другим. Поэтому Spring Data в целом не является ORM.

Spring Data JPA предоставляет репозитории поверх JPA. Разработчик объявляет интерфейс, например наследник `JpaRepository`, а инфраструктура создаёт реализацию. Поддерживаются CRUD, пагинация, сортировка, запросы по именам методов, `@Query` и собственные реализации. SQL и отображение сущностей по-прежнему выполняет JPA-провайдер.

Jakarta Data решает похожую задачу как стандарт Jakarta, а Spring Data относится к экосистеме Spring. Их API не являются взаимозаменяемыми. В моём проекте Spring Data JPA не используется: репозитории напрямую работают с EntityManager.

### 如何证明没用 Spring Data / Как это проверить

检查 `build.gradle`：没有 `spring-boot-starter-data-jpa`；检查 Repository：没有继承 `JpaRepository`，而是明确调用 `em.find/persist/createQuery`。类上有 Spring `@Repository` 并不能证明使用了 Spring Data。

**Русский:** В зависимостях отсутствует starter Spring Data JPA, а классы репозиториев не наследуют `JpaRepository`. Аннотация Spring `@Repository` сама по себе не означает использование Spring Data.

课件依据：C 第 65–76 页，重点第 67–71 页（Repository 与 Service）、第 73–75 页（派生查询）；B 第 61–69 页对比 DAO 与 Jakarta Data。补充：[Spring Data JPA](https://spring.io/projects/spring-data-jpa/)。

## Spring 课件中需要准确理解的简化表述 / Уточнения к презентации Spring

1. **第 13 页：Spring Bean 不必须有无参构造器。** 可通过带参构造器注入；这不同于本项目 JPA Entity 的无参构造要求。 / **Страница 13:** Spring-бину не обязательно иметь конструктор без параметров; доступно внедрение через конструктор. Требования JPA Entity отличаются. [构造器注入](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)
2. **第 57 页：嵌入式 Tomcat 是 Servlet 容器。** 不能据此认为它实现完整 Jakarta EE 平台。 / **Страница 57:** встроенный Tomcat является Servlet-контейнером, а не реализацией полного профиля Jakarta EE.
3. **第 71 页：CrudRepository.findById 返回 Optional。** 不存在时是 Optional.empty()；不要与 EntityManager.find 返回 null 混淆。 / **Страница 71:** `findById` возвращает `Optional`, а не непосредственно Entity или null. [CrudRepository API](https://docs.spring.io/spring-data/commons/docs/3.3.5/api/org/springframework/data/repository/CrudRepository.html)
4. **第 72 页：singleton 是默认作用域，可改变。** 这些注解不强制所有 Bean 永远 singleton；`@Repository` 还可参与持久化异常转换，并非只有名称不同。 / **Страница 72:** singleton — область по умолчанию, её можно изменить. `@Repository` также имеет значение для преобразования исключений доступа к данным.
5. **第 78 页：Spring AOP 与 AspectJ 不能完全等同。** 常见 Spring AOP 使用代理，可以使用 AspectJ 风格注解；使用注解并不意味着启用了 AspectJ 编译期或加载期织入。 / **Страница 78:** Spring AOP обычно основан на прокси; синтаксис аннотаций AspectJ не означает, что включено AspectJ weaving. [Spring AOP 代理机制](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)

这些补充用于把课件的教学概括与本项目实际 API 对齐，答辩时先讲课程概念，再说明具体版本和代码。

**Русский:** Эти уточнения связывают учебные схемы с реальным API проекта. На защите следует сначала объяснить концепцию, затем показать конкретную реализацию.

## 项目答辩速查 / Краткие ответы по проекту

| 中文 | Русский |
|---|---|
| 持久化链：Repository → JPA EntityManager → EclipseLink → JDBC → PostgreSQL。 | Цепочка: Repository → EntityManager JPA → EclipseLink → JDBC → PostgreSQL. |
| 数据库是 city_lab1，schema 是 lab1_info；schema 是库内命名空间。 | База — city_lab1, схема — lab1_info; схема является пространством имён внутри базы. |
| 数据库账号用于连接数据库；网页账号注册后保存在 app_user，两者不同。 | Учётная запись БД используется для соединения; пользователи сайта хранятся в app_user. |
| 密码存 BCrypt 哈希，不存明文；哈希不是可逆加密。 | Хранится BCrypt-хеш пароля, а не открытый пароль; хеширование не является обратимым шифрованием. |
| @Version 防止旧版本覆盖新数据，冲突时返回错误。 | @Version предотвращает перезапись новой версии устаревшими данными. |
| 外键保护被引用对象，删除城市不级联删除共享坐标/省长。 | Внешние ключи защищают связанные объекты; удаление города не удаляет общие координаты и губернатора. |
| revision 轮询用于跨用户刷新，不是 WebSocket。 | Опрос revision обновляет интерфейс между сеансами; WebSocket не используется. |
| 五个特殊操作在 PostgreSQL 函数中计算，Java 仅调用并返回。 | Пять специальных операций вычисляются функциями PostgreSQL, Java вызывает их и возвращает результат. |
| 界面只显示年月日，实体保留实验指定的日期时间类型。 | Интерфейс показывает только дату, а типы полей Entity соответствуют заданию. |

## 建议演示顺序 / Порядок демонстрации

1. 注册并登录，说明会话、CSRF、BCrypt。 / Зарегистрироваться, войти и объяснить сеанс, CSRF и BCrypt.
2. 创建坐标、省长、城市，解释关联。 / Создать координаты, губернатора и город, объяснить связи.
3. 展示校验、筛选、排序、分页与日期选择。 / Показать валидацию, фильтрацию, сортировку, страницы и выбор даты.
4. 双浏览器演示刷新和版本冲突，尝试删除被引用对象。 / Показать обновление, конфликт версий и защиту связанных объектов.
5. 执行五个特殊操作，打开 SQL 函数和 Repository。 / Выполнить пять операций и показать SQL-функции и репозиторий.
6. 打开 PersistenceConfig，说明 JPA、EclipseLink、Spring 的分工。 / Объяснить разделение ролей JPA, EclipseLink и Spring.
