import controller.MainController;
import gui.AuthWindow;
import gui.LanguageSelector;
import gui.MainWindow;
import javafx.application.Application;
import javafx.scene.control.Alert;
import javafx.stage.Stage;
import network.ServerProxy;

import java.net.SocketException;

public class ClientApp extends Application {
    @Override
    public void start(Stage primaryStage) { // 重写 start 方法
        // 第一步：语言选择（需修改 LanguageSelector 为 JavaFX 的 Dialog）
        LanguageSelector selector = new LanguageSelector();
        selector.showAndWait(); // 阻塞直到对话框关闭

        // 第二步：初始化网络连接
        try {
            ServerProxy proxy = getProxy();
            Runtime.getRuntime().addShutdownHook(new Thread(proxy::shutDown));
        } catch (SocketException ex) {
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setContentText("Network Error: " + ex.getMessage());
            alert.show();
        }
    }

    private static ServerProxy getProxy() throws SocketException {
        ServerProxy proxy = new ServerProxy("localhost", 5432);
        proxy.startSyncThread();

        // 第三步：显示认证窗口
        AuthWindow authWindow = new AuthWindow(proxy);
        authWindow.show(); // 使用show()代替setVisible(true)

        // 第四步：主窗口初始化
        MainController controller = new MainController(proxy);
        controller.initialize();

        // 监听认证窗口关闭事件
        authWindow.setOnHiding(event -> {
            MainWindow mainWindow = new MainWindow(proxy, controller);
            mainWindow.show(); // 使用show()代替setVisible(true)
        });

        return proxy;
    }

    public static void main(String[] args) {
        launch(args);
    }
}