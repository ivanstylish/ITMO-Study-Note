### 如何在Helios上部署自己的实验室工作并正常启动
1. 下载并解压 WildFly。您可以在 helios 上运行这些命令：
```
curl https://download.jboss.org/wildfly/21.0.0.Final/wildfly-21.0.0.Final.zip -o wildfly.zip
unzip wildfly.zip -d wildfly
```

2. 将 `war` 上传到 `helios` 并将其放到目录中 `~/wildfly/wildfly-21.0.0.Final/standalone/deployments/` 。

3. 在 `~/wildfly/wildfly-21.0.0.Final/standalone/configuration/standalone.xml` 中，更改：
From  
```
<interface name="public">
    <inet-address value="${jboss.bind.address:127.0.0.1}"/>
</interface>
```
To  
```
<interface name="public">
    <any-address/>
</interface>
```

进一步的任务：  
    - 将默认端口更改为端口库(portbase) 。
    - 重要！更改所有其他端口，以便在服务器启动时不会出现错误(`already in use`)。

From
```
<socket-binding name="http" port="${jboss.http.port:8080}"/>
<socket-binding name="https" port="${jboss.https.port:443}"/>
        ...
        ...
```
To
```
<socket-binding name="http" port="${jboss.http.port:<portbase>}"/>
```

4. 例如，我的端口库是 32318。假设它后面的 99 个端口也是我的，所以我写了任何大于 32318 的端口 1-99，我的 standalone.xml 结果是：
```
<socket-binding name="ajp" port="${jboss.ajp.port:32319}"/>
<socket-binding name="http" port="${jboss.http.port:32318}"/>
<socket-binding name="https" port="${jboss.https.port:32320}"/>
<socket-binding name="management-http" interface="management" port="${jboss.management.http.port:32321}"/>
<socket-binding name="management-https" interface="management" port="${jboss.management.https.port:32322}"/> 
```

5. 连接到 helios，使用以下命令转发端口：
```
ssh -p 2222 s407959@se.ifmo.ru -L <portbase>:helios.cs.ifmo.ru:<portbase>
```
```
ssh -p 2222 s407959@se.ifmo.ru -L 5786:helios.cs.ifmo.ru:5786
yDqY-9700
```

6. 启动服务器
```
bash ~/wildfly-37.0.1.Final/bin/standalone.sh
```

7. 浏览器打开网站
```
http://localhost:5786/area-check/
```