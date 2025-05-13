package gui;

import controller.AuthController;
import javafx.application.Platform;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.stage.Stage;
import network.ServerProxy;
import util.LocalizationManager;

import java.io.IOException;


public class AuthWindow extends Stage {
    private final ServerProxy proxy;
    private final AuthController authController;

    public AuthWindow(ServerProxy proxy) {
        this.proxy = proxy;
        this.authController = new AuthController();
        setupUI();
        setupController();
    }

    private void setupUI() {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/Auth.fxml"));
            loader.setController(authController);  // 手动设置控制器
            Parent root = loader.load();
            this.setScene(new Scene(root, 400, 250));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void setupController() {
        authController.setCallback(() -> Platform.runLater(() -> {
            this.close(); // 关闭认证窗口
            try {
                // 加载主窗口的 FXML 文件，确保路径正确
                FXMLLoader loader = new FXMLLoader(getClass().getResource("/gui/Main.fxml"));
                Parent root = loader.load();
                Stage mainStage = new Stage();
                mainStage.setScene(new Scene(root));
                mainStage.show();
            } catch (IOException e) {
                e.printStackTrace();
                // 显示错误提示
                Alert alert = new Alert(Alert.AlertType.ERROR);
                alert.setContentText("Unable to load the main interface: " + e.getMessage());
                alert.show();
            }
        }));
        authController.setLocalizator(LocalizationManager.getInstance());
        authController.setClient(proxy);
    }
}