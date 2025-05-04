psql -U varnothing -d lab7 -f lab7.sql

psql -U varnothing -h localhost -d lab7

要连接到部门服务器上的数据库，请使用主机pg、数据库名称 - studs、用户名/密码与连接到服务器的匹配。

"jdbc:postgresql://pg:5432/studs"
user = "s407959"
password = "R3JIQIhNsdM2QGJv"

cat ~/.pgpass 获取pgpass

PGPASSWORD= psql -h localhost -p 5432 -U s407959 -d studs

psql -h pg -d studs -U s407959 -W
输入密码 R3JIQIhNsdM2QGJv。

## 如果登录失败，说明密码或登录不正确。 请联系管理员以澄清数据