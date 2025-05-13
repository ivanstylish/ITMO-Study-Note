import controller.MainController;
import gui.AuthWindow;
import gui.LanguageSelector;
import gui.MainWindow;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.control.Alert;
import javafx.stage.Stage;
import network.ServerProxy;

import java.net.SocketException;

public class ClientApp extends Application {
    @Override
    public void start(Stage primaryStage) { // 重写 start 方法
        // 第一步：语言选择

        // 第二步：初始化网络连接

            try {
                ServerProxy proxy = getProxy();
                Runtime.getRuntime().addShutdownHook(new Thread(proxy::shutDown));
            } catch (SocketException ex) {
                Platform.runLater(() -> {
                    Alert alert = new Alert(Alert.AlertType.ERROR);
                    alert.setContentText("Network Error: " + ex.getMessage());
                    alert.show();
                });
            }
        }

    private static ServerProxy getProxy() throws SocketException {
        ServerProxy proxy = new ServerProxy("localhost", 5432);
        proxy.startSyncThread();

        // 第三步：显示认证窗口
        AuthWindow authWindow = new AuthWindow(proxy);
        authWindow.show(); // 使用show()代替setVisible(true)

        // 监听认证窗口关闭事件
        authWindow.setOnHiding(event -> {
            MainWindow mainWindow = new MainWindow(proxy);
            mainWindow.show(); // 使用show()代替setVisible(true)
            authWindow.close();
        });

        return proxy;
    }

    public static void main(String[] args) {
        launch(args);
    }
}