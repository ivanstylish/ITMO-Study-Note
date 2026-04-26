@echo off
REM =============================================================
REM history.bat — 搜索最后可编译的 git 版本（Windows 版）
REM
REM 用法：history.bat <src_dir> <classes_dir> <lib_dir>
REM 由 build.xml 的 history 目标自动调用
REM =============================================================

setlocal enabledelayedexpansion

set SRC_DIR=%1
set CLASSES_DIR=%2
set LIB_DIR=%3

REM 生成时间戳（用于 diff 文件名）
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set TIMESTAMP=%DT:~0,8%_%DT:~8,6%
set DIFF_FILE=broken_diff_%TIMESTAMP%.diff

echo ========================================================
echo  [history] 开始搜索最后可编译的 git 版本
echo  SRC_DIR     = %SRC_DIR%
echo  CLASSES_DIR = %CLASSES_DIR%
echo  LIB_DIR     = %LIB_DIR%
echo ========================================================

REM 检查是否在 git 仓库中
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo [history] 错误：当前目录不是 git 仓库！
    echo [history] 请先执行 git init 并至少提交一次。
    exit /b 1
)

REM 记录当前分支和 HEAD
for /f %%i in ('git rev-parse HEAD') do set ORIGINAL_REV=%%i
for /f %%i in ('git rev-parse --abbrev-ref HEAD') do set ORIGINAL_BRANCH=%%i
echo [history] 当前分支：%ORIGINAL_BRANCH%
echo [history] 当前提交：%ORIGINAL_REV%

REM 构建 classpath（lib/compile 下所有 jar）
set CP_STR=
if exist "%LIB_DIR%" (
    for %%f in ("%LIB_DIR%\*.jar") do (
        if "!CP_STR!"=="" (
            set CP_STR=%%f
        ) else (
            set CP_STR=!CP_STR!;%%f
        )
    )
)
echo [history] Classpath：%CP_STR%
echo --------------------------------------------------------

REM 获取所有 commit hash（跳过第一个，即 HEAD）
set INDEX=0
set LAST_WORKING=
set LAST_WORKING_INDEX=-1
set NEXT_BROKEN=

REM 把所有 commit 存入临时文件
git log --format="%%H" HEAD > %TEMP%\git_revs.txt

REM 读取 commit 列表，从第 2 个开始（跳过 HEAD）
set /a LINE_NUM=0
for /f %%H in (%TEMP%\git_revs.txt) do (
    set /a LINE_NUM+=1
    if !LINE_NUM! gtr 1 (
        set REV=%%H
        set REV_SHORT=!REV:~0,8!

        REM 获取提交信息
        for /f "delims=" %%M in ('git log --format^="%%s" -1 !REV! 2^>nul') do set MSG=%%M

        echo [history] [!LINE_NUM!] 检查：!REV_SHORT! - !MSG!

        REM checkout 到该 commit
        git checkout --quiet !REV! 2>nul

        REM 清空输出目录
        if exist "%CLASSES_DIR%_test" rmdir /s /q "%CLASSES_DIR%_test"
        mkdir "%CLASSES_DIR%_test" 2>nul

        REM 收集所有 .java 文件
        set JAVA_LIST=%TEMP%\java_files.txt
        dir /s /b "%SRC_DIR%\*.java" > !JAVA_LIST! 2>nul

        REM 尝试编译
        if "!CP_STR!"=="" (
            javac -d "%CLASSES_DIR%_test" -encoding UTF-8 --release 17 @!JAVA_LIST! >nul 2>&1
        ) else (
            javac -cp "!CP_STR!" -d "%CLASSES_DIR%_test" -encoding UTF-8 --release 17 @!JAVA_LIST! >nul 2>&1
        )

        if !errorlevel! == 0 (
            echo [history] FOUND 找到可编译版本：!REV_SHORT!
            set LAST_WORKING=!REV!
            set LAST_WORKING_INDEX=!LINE_NUM!
            goto :found
        ) else (
            echo [history] 编译失败，继续回溯...
        )
    )
)

echo [history] 所有历史版本均无法编译！
git checkout --quiet %ORIGINAL_REV% 2>nul
git checkout --quiet %ORIGINAL_BRANCH% 2>nul
exit /b 2

:found
REM 清理临时测试目录
if exist "%CLASSES_DIR%_test" rmdir /s /q "%CLASSES_DIR%_test"

REM 找到"破坏编译的那个提交"= LAST_WORKING 的前一个 commit（即 index-1）
set /a NEXT_INDEX=%LAST_WORKING_INDEX% - 1
set NEXT_LINE=0
set NEXT_BROKEN=%ORIGINAL_REV%

if %NEXT_INDEX% gtr 1 (
    for /f %%H in (%TEMP%\git_revs.txt) do (
        set /a NEXT_LINE+=1
        if !NEXT_LINE! == %NEXT_INDEX% (
            set NEXT_BROKEN=%%H
        )
    )
)

echo --------------------------------------------------------
echo  [history] 结果：
echo    最后可编译版本  ：%LAST_WORKING:~0,8%
echo    破坏编译的版本  ：%NEXT_BROKEN:~0,8%
echo --------------------------------------------------------

REM 生成 diff 文件
echo [history] 生成 diff 文件：%DIFF_FILE%
(
    echo # Diff：最后可编译版本 vs 破坏编译的版本
    echo # 可编译版本  ：%LAST_WORKING%
    echo # 破坏编译版本：%NEXT_BROKEN%
    echo # 生成时间    ：%DATE% %TIME%
    echo # ================================================================
    git diff %LAST_WORKING% %NEXT_BROKEN%
) > %DIFF_FILE%

echo [history] Diff 已写入：%DIFF_FILE%

REM 返回到原始分支
git checkout --quiet %ORIGINAL_REV% 2>nul
git checkout --quiet %ORIGINAL_BRANCH% 2>nul
echo [history] 已返回到原始分支：%ORIGINAL_BRANCH%

echo ========================================================
echo  [history] 完成！
echo  建议：打开 %DIFF_FILE% 查看破坏编译的具体改动
echo  回滚命令：git checkout %LAST_WORKING:~0,8%
echo ========================================================

endlocal
exit /b 0