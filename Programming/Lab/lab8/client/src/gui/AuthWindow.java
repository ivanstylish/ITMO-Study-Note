package gui;

import controller.AuthController;
import controller.MainController;
import network.ServerProxy;
import util.LocalizationManager;

import javafx.application.Platform;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.GridPane;
import javafx.stage.Stage;


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
        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(10);

        // 添加组件：登录字段、密码字段、按钮等
        Label loginLabel = new Label(LocalizationManager.getString("LoginField"));
        TextField loginField = new TextField();
        Label passwordLabel = new Label(LocalizationManager.getString("PasswordField"));
        PasswordField passwordField = new PasswordField();
        Button loginButton = new Button(LocalizationManager.getString("Login"));
        Button registerButton = new Button(LocalizationManager.getString("SignUpButton"));

        grid.add(loginLabel, 0, 0);
        grid.add(loginField, 1, 0);
        grid.add(passwordLabel, 0, 1);
        grid.add(passwordField, 1, 1);
        grid.add(loginButton, 0, 2);
        grid.add(registerButton, 1, 2);

        Scene scene = new Scene(grid, 400, 250);
        this.setScene(scene);
        this.setTitle(LocalizationManager.getString("AuthTitle"));
    }

    private void setupController() {
        // 绑定控制器逻辑（参考原 AuthWindow 的 setupController()）
        authController.setCallback(() -> {
            Platform.runLater(() -> {
                this.close();
                MainController mainController = new MainController(proxy);
                MainWindow mainWindow = new MainWindow(proxy, mainController);
                mainWindow.show();
            });
        });
        authController.setLocalizator(LocalizationManager.getInstance());
        authController.setClient(proxy);
        authController.initialize();
    }
}