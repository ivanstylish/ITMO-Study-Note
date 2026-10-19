# 学校远程服务器部署

**客户端就是浏览器。JAR 内已经包含登录页、主页、JavaScript 和 CSS，不需要再单独部署前端。**

把 JAR 上传到学校服务器后，端口不会因为上传自动改变。浏览器地址中的 `localhost` 始终表示运行该浏览器的电脑，所以在自己的电脑上输入 `localhost:8080`，不会自动访问学校服务器。推荐先建立 SSH 隧道，再从本机浏览器打开页面。

当前项目中有两个不同的默认值，选择哪种启动方法，就按对应的端口连接：

| 启动方法 | 未额外指定端口时的监听地址 | 说明 |
|---|---|---|
| 直接执行 `java -jar build/libs/city-lab1.jar` | `127.0.0.1:8080` | 来自 `src/main/resources/application.yml` |
| 执行 `sh scripts/run-server.sh` | `127.0.0.1:18080` | 脚本设置了 `PORT=18080` 的默认值 |
| 设置 `PORT=18081` 后启动 | `127.0.0.1:18081` | 以实际指定的 `PORT` 为准 |

上述默认监听地址 `127.0.0.1` 只接受**服务器本机**连接，因此适合配合 SSH 隧道。若端口被占用，应用会启动失败，不会自动寻找另一个端口。本文后续统一采用服务器应用端口 `18080`、本机浏览器端口 `8080`。

下文的 SCHOOL_HOST、SSH_PORT、sXXXXXX、18080 是需要按学校账户信息替换的示例。
题目只给出了数据库主机 pg、数据库 studs，没有给出 SSH 主机名或 SSH 端口，因此不能把示例当作学校真实地址。

## 1. 在本地打包

在 IDEA 的项目终端（PowerShell）执行：

```powershell
.\gradlew.bat clean test bootJar
```

结果：build/libs/city-lab1.jar。它是可执行 JAR，嵌入 Tomcat；不需要部署为 WAR，也不需要把 EclipseLink 等依赖一个个上传。
test 执行不依赖数据库的测试；integrationTest 需要专门的测试数据库，不能直接针对学校 studs 运行。

如教师要求提交源代码，可在 IDEA 外用资源管理器压缩 Lab1 文件夹，或执行：

```powershell
Compress-Archive -Path .\src,.\gradle,.\gradlew,.\gradlew.bat,.\build.gradle,.\settings.gradle,.\README.md,.\docs,.\scripts,.\compose.yaml -DestinationPath ..\Lab1-source.zip
```

不要上传 .gradle、IDEA 缓存或带真实密码的文件。提交源码 ZIP 和运行 JAR 是不同用途，通常二者都可以保留。

## 2. 上传 JAR

先创建远程目录：

```powershell
ssh -p SSH_PORT sXXXXXX@SCHOOL_HOST "mkdir -p ~/InformationSystem/Lab1/build/libs ~/InformationSystem/Lab1/scripts"
scp -P SSH_PORT .\build\libs\city-lab1.jar sXXXXXX@SCHOOL_HOST:~/InformationSystem/Lab1/build/libs/
scp -P SSH_PORT .\scripts\run-server.sh sXXXXXX@SCHOOL_HOST:~/InformationSystem/Lab1/scripts/
```

ssh 的端口参数是小写 -p，scp 是大写 -P。默认端口 22 时可以省略参数。也可以使用 WinSCP，通过 SFTP 把这两个文件上传到对应目录。

## 3. 登录并确认运行环境

```sh
ssh -p SSH_PORT sXXXXXX@SCHOOL_HOST
java -version
```

需要 Java 17。若系统默认 Java 较旧，使用学校已经提供的 Java 17 的绝对路径，或者按学校说明设置 PATH。JAR 不能用 Java 8/11 运行。
学校如果要求额外跳板机、VPN、指定应用端口，以学校配置为准；本项目不依赖某个固定 SSH 主机名。

## 4. 配置学校数据库与网页账号

以下交互命令在 **Bash** 中执行；如果登录后的默认 shell 不是 Bash，先输入 bash（前提是服务器安装了 Bash）。

```bash
cd ~/InformationSystem/Lab1
export DB_USER='sXXXXXX'
read -r -s -p 'Database password: ' DB_PASSWORD
echo
export DB_PASSWORD

export DB_URL='jdbc:postgresql://pg:5432/studs'
export DB_SCHEMA='sXXXXXX_lab1'
export PORT='18080'
export SERVER_ADDRESS='127.0.0.1'

sh scripts/run-server.sh
```

- DB_USER、DB_PASSWORD 使用学校分配的数据库账号及其密码；不要把本机数据库密码直接当作学校数据库密码。如果学校说明它们与服务器登录凭据一致，按学校说明填写。
- pg 是学校内部数据库主机，通常不能在你本地直接解析；上述 URL 用在远程运行的应用。
- 本机项目的默认 schema 保持 `lab1_info`。此处的远程示例通过 DB_SCHEMA 单独指定个人 schema，避免多人在共享 studs 数据库中使用同名表；例如 s123456_lab1。如果学校允许且该 schema 归你管理，也可以继续使用 `lab1_info`。名称采用普通小写字母、数字、下划线。
- Hikari 的 schema 设置负责应用访问范围，Flyway 在同一 schema 创建表与函数；实体和函数调用不写死某个学生的 schema。
- 如果账号没有 CREATE SCHEMA 权限，请使用学校已分配给你的 schema，例如把 DB_SCHEMA 改成 sXXXXXX；该 schema 中应不存在同名实验表。不要给共享数据库执行 DROP SCHEMA 或清空表。
- Flyway 可以在自己有权限的 schema 内自动完成初始化；不需要创建新的数据库，数据库名始终是 studs。
- 启动后在网页点击 Регистрация 注册应用账号。网页密码与数据库密码分开。

看到 Started CityApplication 后，说明服务已启动。首次建议在前台运行，方便看到数据库权限、密码或端口冲突的错误。

如果只上传了 JAR，没有上传脚本，在上面已经设置环境变量的同一个 Bash 会话中，可以改用下面的命令启动。两种启动命令选一种即可：

```bash
java -Duser.timezone=UTC -jar build/libs/city-lab1.jar --server.address=127.0.0.1 --server.port=18080
```

这里显式指定应用端口为 `18080`。不传 `--server.port` 且没有设置 `PORT` 时，直接运行 JAR 才会使用配置文件中的 `8080`。启动后可在服务器另一个 SSH 会话中执行 `curl -I http://127.0.0.1:18080/login`，检查网页服务是否响应。

## 5. 从本地浏览器访问：SSH 隧道

在本地另外打开一个 PowerShell，保持远程应用仍在运行：

```powershell
ssh -p SSH_PORT -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8080:127.0.0.1:18080 sXXXXXX@SCHOOL_HOST
```

然后访问 [http://localhost:8080/login](http://localhost:8080/login)，也可以使用 [http://127.0.0.1:8080/login](http://127.0.0.1:8080/login)。

该命令把你电脑的 8080 端口转发到远程服务器的 127.0.0.1:18080。应用仍在学校服务器上执行，PostgreSQL 也由服务器连接；浏览器只是通过 SSH 隧道访问页面。

| 命令中的部分 | 含义 | 是否必须与浏览器端口相同 |
|---|---|---|
| `-p SSH_PORT` | 学校 SSH 服务的端口，例如学校实际提供的 `22` 或 `2222` | 否 |
| `-N` | 只建立隧道，不打开远程命令行 | 不适用 |
| `ExitOnForwardFailure=yes` | 本地监听端口绑定失败时，直接退出并显示错误 | 不适用 |
| `-L` 后的第一个 `127.0.0.1:8080` | 你自己电脑上的隧道入口 | 是，浏览器访问这里 |
| 最后一个 `127.0.0.1:18080` | 从学校 SSH 服务器连接的应用地址 | 否，但必须等于远程应用的实际监听地址 |

SSH 端口、远程应用端口、本机浏览器端口是三件独立的事。它们可以不同；不能把 SSH 的 `2222` 当成网页端口。`-L` 与 `-N` 的含义见 [OpenSSH 官方手册](https://man.openbsd.org/ssh)。

隧道窗口需要保持打开。若本地 `8080` 已被 IDEA 中运行的项目占用，改用本地 `8081`：

```powershell
ssh -p SSH_PORT -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8081:127.0.0.1:18080 sXXXXXX@SCHOOL_HOST
```

这时浏览器访问 [http://localhost:8081/login](http://localhost:8081/login)，远程应用仍然使用 `18080`。若远程应用使用 `8080`，只把命令最后的 `18080` 改成 `8080`。

如果学校明确分配了可直接访问的应用端口，则按学校要求将应用监听地址设为 `SERVER_ADDRESS=0.0.0.0`，浏览器访问 `http://学校服务器域名:应用端口/login`。这还要求学校网络和防火墙允许该端口。`0.0.0.0` 是监听配置，不是应该输入浏览器的服务器地址；学校提供了反向代理网址时，以该网址为准。

## 6. 后台运行和停止

确认前台启动成功后，Ctrl+C 停止，再在**仍保留环境变量的同一个 Bash 会话**中执行：

```bash
nohup sh scripts/run-server.sh > app.log 2>&1 &
echo $! > app.pid
tail -n 80 app.log
```

nohup 使进程在 SSH 断开后继续运行，app.log 保存日志。学校可能限制后台进程时长，以学校规定为准。

停止自己启动的应用：

```bash
kill "$(cat app.pid)"
```

使用前确认 app.pid 属于当前运行实例；不要终止其他用户或无关 Java 进程。应用停止后，数据库数据仍保留。

## 7. 如果必须在服务器上从源码构建

上传并解压源码 ZIP 后：

```sh
cd ~/InformationSystem/Lab1
chmod +x gradlew
./gradlew test bootJar
```

需要服务器能够访问 Gradle 分发站和依赖仓库。学校服务器若禁止外网访问，选择本地构建后上传 JAR；运行 JAR 不需要联网下载 Gradle 或依赖。

## 8. 常见问题

| 现象 | 处理 |
|---|---|
| password authentication failed | 检查 DB_USER/DB_PASSWORD，学校账户与应用网页账户不是同一套 |
| UnknownHostException: pg | pg 是校内名称；在学校服务器运行，或使用学校允许的数据库隧道 |
| permission denied for schema | DB_SCHEMA 设为自己有权限的 schema |
| relation already exists / Flyway 初始化报错 | 使用个人专用空 schema；不要覆盖以前实验或他人表 |
| Flyway checksum mismatch | 历史迁移被修改了；对已有数据库应新增后续编号的迁移，不能随意 repair 掩盖差异 |
| Address already in use | 换一个学校允许且尚未占用的 PORT，隧道右侧端口同步修改 |
| UnsupportedClassVersionError | 当前 Java 低于 17；检查实际调用的 java 路径 |
| Gradle Java toolchain missing | 本地安装 JDK 17，并在 IDEA 中设置 Gradle JVM |
| 页面无法打开但服务器已启动 | 检查 SSH 隧道仍打开，左侧和右侧端口匹配 |
| 打开后看到的还是本地旧页面 | 检查本地 `8080` 是否已有 IDEA 项目占用；隧道改为本地 `8081` 后访问该地址 |
| administratively prohibited | 学校 SSH 服务可能不允许端口转发，按学校提供的访问方式配置 |
| 删除返回 409 | 对象被引用或版本过期，按界面提示解除关联/重新打开 |

命令参数依据：[OpenSSH ssh 手册](https://man.openbsd.org/ssh)、[OpenSSH scp 手册（`-P` 指定端口）](https://man.openbsd.org/OpenBSD-7.0/scp.1)。

