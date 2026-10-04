登录：ssh s407959@helios.cs.ifmo.ru -p 2222 
==注意==：如果使用VPN或在学校内网,就需要把端口名换为IP地址 -> (192.168.10.80)  
上传：scp -P 2222 ds.txt s407959@helios.cs.ifmo.ru:~/  
下载：scp -P 2222 s407959@helios.cs.ifmo.ru:~/ds.txt ds.txt  
密码：yDqY-9700  

> VPN:  
s407959  
Zjj189481#  

> openVPN:  
s407959  
yDqY-9700  

> 关于数据库：  
PGAdmin4
cat ~/.pgpass ; 获数据库密码  
PGPASSWORD=R3JIQIhNsdM2QGJv  
连接学校数据库：  
psql -h pg -d studs  
psql -h pg -d ucheb  

> 查看学校jdk版本   
pkg info | grep openjdk  

> 切换jdk版本  
export JAVA_HOME=/usr/local/openjdk21(17)  
export PATH=$JAVA_HOME/bin:$PATH  

java -Xmx128m -XX:+UseSerialGC -jar client.jar   
pgpassword=R3JIQIhNsdM2QGJv  

COLLECTION_FILE=$HOME/data.json java -jar Lab5.jar  

COLLECTION_FILE=$HOME/data.json java -jar Server_jar/Server.jar  

claude --settings D:/Study-Note/claude-deepseek-settings.json --bare

s407956
ssh s407956@helios.cs.ifmo.ru -p 2222 
GCrx<1558

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 's407956'
    LOOP
        EXECUTE format(
            'DROP TABLE IF EXISTS %I.%I CASCADE',
            's407956',
            r.tablename
        );
    END LOOP;
END $$;

psql -h helios.se.ifmo.ru -p 5432 -U s407956 -d studs -W