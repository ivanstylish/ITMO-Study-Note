docker run -d \
  --name oracle-xe \
  -p 1521:1521 \
  -e ORACLE_PASSWORD=R3JIQIhNsdM2QGJv \
  -v oracle-data:/opt/oracle/oradata \
  gvenzl/oracle-xe:21-full

//查看运行状态 `docker ps`
//若没启动，手动启动 `docker start oracle-xe`
docker run -d --name oracle-xe -p 1521:1521 -e ORACLE_PASSWORD=R3JIQIhNsdM2QGJv -v oracle-data:/opt/oracle/oradata gvenzl/oracle-xe:21-full  


docker exec -it oracle-xe sqlplus sys/R3JIQIhNsdM2QGJv@XE as sysdba

ALTER SESSION SET CONTAINER = XEPDB1;  -- 切换到应用推荐的 PDB

CREATE USER s407959 IDENTIFIED BY R3JIQIhNsdM2QGJv;
GRANT CONNECT, RESOURCE, CREATE VIEW TO s407959;
ALTER USER s407959 QUOTA UNLIMITED ON USERS;

TRUNCATE TABLE APP_USER; // 清空表
EXIT;
