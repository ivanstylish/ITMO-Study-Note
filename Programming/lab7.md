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