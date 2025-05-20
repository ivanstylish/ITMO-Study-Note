@echo off
setlocal

:: JavaFX SDK 路径（请不要加 \lib，这里是完整路径）
set PATH_TO_FX=D:\javafx-sdk-17.0.15\lib

:: 输出目录
set OUT_DIR=out

:: 编译入口类（自动连带依赖）
echo [1] 编译 Java 程序...
javac --module-path "%PATH_TO_FX%" --add-modules javafx.controls,javafx.fxml -d %OUT_DIR% client\src\main\java\client\App.java

if %errorlevel% neq 0 (
    echo 编译失败，请检查源码或路径。
    pause
    exit /b
)

:: 运行程序
echo [2] 启动程序...
java --module-path "%PATH_TO_FX%" --add-modules javafx.controls,javafx.fxml -cp %OUT_DIR% client.App

endlocal
pause
