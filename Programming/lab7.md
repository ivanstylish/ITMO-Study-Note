### Вопросы к защите лабораторной работы:

sequenceDiagram
    participant Client
    participant UDPChannelManager
    participant RequestHandler
    participant CommandProcessor
    participant ProductDAO
    
    Client->>UDPChannelManager: 发送请求数据
    UDPChannelManager->>RequestHandler: 传递请求
    RequestHandler->>CommandProcessor: 处理命令
    CommandProcessor->>ProductDAO: 数据库操作
    ProductDAO-->>CommandProcessor: 返回结果
    CommandProcessor-->>RequestHandler: 生成响应
    RequestHandler-->>UDPChannelManager: 返回响应
    UDPChannelManager-->>Client: 发送响应


**模块结构**

1. Common模块：
   - 包含共享类：CommandRequest, CommandResponse, Product, Coordinates等。

   - 工具类：SerializationUtil, HashUtil。

2. Client模块：

   - 用户交互：InteractiveShell, InputHandler。

   - 网络代理：ServerProxy发送请求。

3. Server模块：

   - 网络层：UDPChannelManager接收请求，RequestHandler处理请求。

   - 数据层：ProductDAO, OrganizationDAO操作数据库。


**数据传输流程**

1. 客户端发送请求：

   - 用户输入命令（如add），InputHandler构造Product对象。

   - ServerProxy序列化CommandRequest并通过UDP发送到服务端。

2. 服务端处理请求：

   - UDPChannelManager接收请求并交给RequestHandler。

   - RequestHandler反序列化请求，调用对应的CommandHandler（如AddHandler）。

   - AddHandler通过productDAO.save()保存数据到数据库。

3. 数据库操作：

   - ProductDAO执行SQL插入操作，并关联CoordinatesDAO和OrganizationDAO


+----------------+       +----------------+       +----------------+
|   Client       |       |   Server       |       |   Database     |
|----------------|       |----------------|       |----------------|
| 1. 用户输入     |  -->  | 2. 接收请求     |  -->  | 3. 执行SQL插入  |
| 5. 显示结果     |  <--  | 4. 返回响应     |  <--  |                |
+----------------+       +----------------+       +----------------+


1. Многопоточность. Класс `Thread`, интерфейс `Runnable`. Модификатор `synchronized`. 多线程。 类 `Thread`, 接口 `Runnable`. 修改器 `synchronised`。
Многопоточные программы расширяют концепцию многозадачности на более низком уровне: программа выполняет несколько задач одновременно. Обычно каждая задача называется потоком, что сокращенно означает управление потоком.  
多线程程序在较低的层次上扩展了多任务的概念：一个程序同时执行多个任务。通常，每一个任务称为一个线程(thread), 它是线程控制的简称。  
实现`Runnable`接口的方式：
- 定义一个类`MyRunnable`，实现`Runnable`接口
- 重写`run()`方法，在`run()`方法中定义线程要执行的任务。
- 创建`MyRunnable`类的实例，并将其作为参数传递给`Thread`类的构造器。

Что такое `synchronised`? За пределами программирования это означает некоторую настройку, которая позволяет двум устройствам или программам работать вместе.  
什么是 "同步"？ 在编程之外，它指的是允许两个设备或程序一起工作的一些设置。  
Если блок кода помечен ключевым словом synchronized, это означает, что он может выполняться только одним потоком одновременно.  
如果代码块标有同步关键字，则表示一次只能由一个线程执行。

2. Методы `wait()`, `notify()` класса `Object`, интерфейсы `Lock` и `Condition`. 对象 "类、接口 `Lock` 和 `condition` 的方法 wait()、"notify()"。


3. Классы-сихронизаторы из пакета `java.util.concurrent`. `java.util.concurrent` 包中的同步器类。

4. Модификатор `volatile`. Атомарные типы данных и операции.  `易失性`修改器。 原子数据类型和操作

5. Коллекции из пакета `java.util.concurrent`.  来自 `java.util.concurrent` 软件包的集合。

6. Интерфейсы `Executor`, `ExecutorService`, `Callable`, `Future` 接口 `Executor`, `ExecutorService`, `Callable`, `Future

7. Пулы потоков 流水池

8. `JDBC`. Порядок взаимодействия с базой данных. Класс `DriverManager`. Интерфейс `Connection`  与数据库交互的顺序。 类 `DriverManager`. 接口 `Connection`.

9. Интерфейсы `Statement`, `PreparedStatement`, `ResultSet`, `RowSet`  接口 `Statement`, `PreparedStatement`, `ResultSet`, `RowSet`

10. Шаблоны проектирования. 设计模式