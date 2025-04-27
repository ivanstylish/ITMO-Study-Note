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