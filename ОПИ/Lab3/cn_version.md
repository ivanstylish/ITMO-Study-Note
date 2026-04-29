# 实验说明 — Apache Ant 构建脚本
## 项目：CoordinateCheck（Jakarta EE + JSF + JPA）
## 课程：Web 编程 · 实验三扩展

---

## 一、实验本质理解

> 在网编实验三的源码基础上，**增加一套自动化构建脚本**，
> 用一条命令替代你原本手动执行的所有操作。

```
你原来手动做的事              →   Ant 自动完成
─────────────────────────────────────────────────
javac 一堆 .java 文件         →   ant compile
javac + jar 打包              →   ant build
rm -rf build/ 清理            →   ant clean
手动跑 JUnit 测试             →   ant test
播放一首音乐庆祝              →   ant music（build 成功后自动触发）
git 回滚找能编译的版本        →   ant history（最复杂，含循环逻辑）
```

**核心考察点**：构建自动化思想 + Ant XML 语法 + Shell/Bat 脚本编写

---

## 二、项目目录结构（按此创建）

```
你的项目根目录/
│
├── build.xml                        ← ★ 主 Ant 脚本
├── build.properties                 ← ★ 所有变量和常量
├── history.bat                      ← ★ Windows 版 history 脚本
│
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── org/coordinate/
│   │   │       ├── bean/
│   │   │       │   ├── ClockBean.java
│   │   │       │   ├── PointBean.java
│   │   │       │   ├── ResultBean.java
│   │   │       │   └── ResultDTO.java
│   │   │       ├── entity/
│   │   │       │   └── Result.java
│   │   │       └── service/
│   │   │           └── AreaCheck.java
│   │   ├── resources/
│   │   │   └── META-INF/
│   │   │       └── persistence.xml
│   │   └── webapp/
│   │       ├── WEB-INF/
│   │       │   ├── beans.xml
│   │       │   ├── faces-config.xml
│   │       │   └── web.xml
│   │       ├── resources/
│   │       │   ├── css/style.css
│   │       │   └── js/main.js
│   │       ├── index.xhtml
│   │       └── main.xhtml
│   │
│   └── test/
│       └── java/
│           └── org/coordinate/service/
│               └── AreaCheckTest.java  
│
├── lib/
│   ├── compile/                    
│   │   └── jakarta.jakartaee-api-10.0.0.jar
│   └── test/
│       └── junit-platform-console-standalone-1.10.0.jar
│
├── resources/
│   └── my-music.wav             
│
└── build/                       
    ├── classes/
    ├── dist/
    └── test/
```

---

## 三、验证 Ant 是否安装成功（CMD）

打开 **命令提示符（cmd）**，输入：

```cmd
ant -version
```

**期望输出**（类似）：
```
Apache Ant(TM) version 1.10.14 compiled on August 31 2023
```

如果提示 `'ant' 不是内部或外部命令`，说明需要配置环境变量：

```
1. 下载 Ant：https://ant.apache.org/bindownload.cgi
   → 选择 apache-ant-1.10.x-bin.zip

2. 解压到，例如：C:\apache-ant-1.10.14\

3. 配置环境变量：
   → 系统属性 → 高级 → 环境变量
   → 新建系统变量：
      变量名：ANT_HOME
      变量值：C:\apache-ant-1.10.14

   → 编辑 Path，新增：
      %ANT_HOME%\bin

4. 重新打开 cmd，再次运行 ant -version
```

---

## 四、使用自己的本地 WAV 音乐文件

**完全可以！** 只需修改 `build.properties` 中的一行：

```properties
# 把这里改成你的 WAV 文件路径（两种写法都可以）

# 方式1：相对路径（推荐，文件放在项目 resources/ 目录下）
music.file=resources/my-music.wav

# 方式2：绝对路径（直接用你电脑上的文件）
music.file=C:/Users/你的用户名/Music/my-favorite-song.wav
```

> **注意**：Windows 路径用正斜杠 `/` 或双反斜杠 `\\`，
> 不要用单个反斜杠 `\`

Windows 播放方式（已在 `build.xml` 中配置）使用 PowerShell：
```xml
powershell -c (New-Object Media.SoundPlayer 'your.wav').PlaySync()
```
这是 Windows 原生方式，**不需要安装任何软件**。

---

## 五、在 CMD 中运行各个目标

进入项目根目录（`build.xml` 所在目录）：

```cmd
cd C:\你的项目路径
```

| 命令 | 功能 |
|------|------|
| `ant compile` | 编译所有 Java 源文件 |
| `ant build` | 编译 + 打包 JAR（成功后自动播放音乐）|
| `ant clean` | 删除 build/ 目录和临时文件 |
| `ant test` | 运行 JUnit 测试（先调用 build）|
| `ant history` | 编译失败时回溯 git 找最后可用版本 |
| `ant clean build` | 清理后重新完整构建 |

---

## 六、下载所需的依赖 JAR

### 6.1 Jakarta EE API（编译用）

前往 Maven 仓库手动下载，放入 `lib/compile/`：

```
https://repo1.maven.org/maven2/jakarta/platform/jakarta.jakartaee-api/10.0.0/jakarta.jakartaee-api-10.0.0.jar
```

### 6.2 JUnit 5 Standalone（测试用）

放入 `lib/test/`：

```
https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.10.0/junit-platform-console-standalone-1.10.0.jar
```

---

## 七、生成的 MANIFEST.MF 内容

`ant build` 会自动在 JAR 包中生成：

```
Manifest-Version: 1.0
Implementation-Title: CoordinateCheck
Implementation-Version: 1.0.0
Implementation-Vendor: ITMO University
Main-Class: org.coordinate.bean.PointBean
Built-By: 你的用户名
Build-Jdk: 17.x.x
```

---

## 八、history 目标的工作原理

```
ant history 被调用
       ↓
尝试编译当前代码
       ↓
  编译成功? ──→ YES → 输出"无需回滚"，结束
       ↓ NO
调用 history.bat（Windows）
       ↓
获取所有 git 提交列表（从新到旧）
       ↓
从上一个提交开始循环：
  ┌──────────────────────────────┐
  │  git checkout <某个提交>     │
  │  尝试 javac 编译             │
  │  编译成功? → 记录为 LAST_OK  │
  │             跳出循环         │
  │  编译失败? → 继续下一个提交  │
  └──────────────────────────────┘
       ↓
找到 LAST_OK？
  YES → 计算下一个提交（破坏编译的那个）
      → git diff LAST_OK NEXT > broken_diff_时间戳.diff
      → 输出报告
  NO  → 输出"所有历史版本都无法编译"
       ↓
git checkout 回到原始分支
```

---

## 九、常见问题

**Q: `ant` 命令找不到？**
A: 检查环境变量 `ANT_HOME` 和 `Path` 是否配置正确，重启 cmd。

**Q: 编译报错找不到 jakarta 包？**
A: 确认 `lib/compile/` 目录下有 `jakarta.jakartaee-api-10.0.0.jar`。

**Q: 音乐不播放？**
A: 检查 `build.properties` 中 `music.file` 路径是否正确，WAV 文件是否存在。

**Q: history 目标报错"不是 git 仓库"？**
A: 确保项目目录已初始化 git（`git init` + 至少一个提交）。

**Q: test 目标报错找不到测试类？**
A: 确认 `AreaCheckTest.java` 放在 `src/test/java/org/coordinate/service/` 目录下。