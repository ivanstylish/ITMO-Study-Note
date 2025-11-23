1. 本地打开网址：`(http://localhost:8080/lab3-1.0/index.xhtml)`

### Helios
1. 转发端口
```
ssh -p 2222 s407959@se.ifmo.ru -L 5786:helios.cs.ifmo.ru:5786
yDqY-9700
```

2. 启动服务器
```
bash ~/wildfly-37.0.1.Final/bin/standalone.sh
```

3. 浏览器打开网站
```
http://localhost:5786/lab3-1.0/index.xhtml