
ssh -L <ВЫДАННЫЙ ВАМ ПОРТ>:localhost:<ВЫДАННЫЙ ВАМ ПОРТ> s<ВАШ ИСУ>@helios.cs.ifmo.ru -p 2222

在Helios上的文件结构：
```
~/
  httpd-root/
    conf/
      httpd.conf # тот самый httpd-helios.conf
    fcgi-bin/
      app.jar
    mutex-dir/ # оставить пустой
    
  .www/(web) # is mine
```

-----------------------------------------
### 程序启动

1. 首先转移端口到本地：
ssh -L 24666:localhost:24666 s407959@helios.cs.ifmo.ru -p 2222
ssh -L 24666:localhost:24666 s407959@192.168.10.80 -p 2222
192.168.10.80
yDqY-9700

2. 然后启动本地的HTTP服务器：
httpd -f ~/httpd-root/conf/httpd.conf -k start

3. 最后启动Jar文件：
java -jar -DFCGI_PORT=24667 ~/httpd-root/fcgi-bin/Lab1.jar

4. 打开浏览器输入+你自己在conf文件设定的端口号
http://localhost:24666/