登录：ssh s407959@helios.cs.ifmo.ru -p 2222
上传：scp -P 2222 ds.txt s407959@helios.cs.ifmo.ru:~/
下载：scp -P 2222 s407959@helios.cs.ifmo.r
u:~/ds.txt ds.txt
yDqY-9700

VPN:
s407959
Zjj18948165786@

cat ~/.pgpass
PGPASSWORD=R3JIQIhNsdM2QGJv
连接学校数据库：
psql -h pg -d studs
psql -h pg -d ucheb

// 查看学校jdk版本
pkg info | grep openjdk

// 切换jdk版本
export JAVA_HOME=/usr/local/openjdk21(17)
export PATH=$JAVA_HOME/bin:$PATH

java -Xmx128m -XX:+UseSerialGC -jar client.jar pgpassword=R3JIQIhNsdM2QGJv

COLLECTION_FILE=$HOME/data.json java -jar Lab5.jar

COLLECTION_FILE=$HOME/data.json java -jar Server_jar/Server.jar
