package controller;

import auth.AuthProvider;
import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import commandUtil.CommandType;
import exception.NetworkException;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import model.Product;
import network.ServerProxy;
import user.User;
import util.DataUpdateEvent;
import util.Event;
import util.LocalizationManager;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.ResourceBundle;

public class AuthController {
    private Runnable callback;
    private LocalizationManager localizator;
    private ServerProxy proxy;
    private final Map<String, Locale> LANGUAGE_MAP = Map.of(
            "English (UK)", Locale.UK,
            "Русский", new Locale("ru"),
            "Македонски", new Locale("mk"),
            "Dansk", new Locale("da")
    );

    @FXML
    private Label titleLabel;
    @FXML
    private TextField loginField;
    @FXML
    private PasswordField passwordField;
    @FXML
    private CheckBox registerButton;
    @FXML
    private Button submitButton;
    @FXML
    private ComboBox<String> languageComboBox;

    @FXML
    public void initialize() {
        languageComboBox.setItems(FXCollections.observableArrayList(LANGUAGE_MAP.keySet()));

        languageComboBox.setValue(AuthProvider.getCurrentLanguage());
        languageComboBox.setStyle("-fx-font: 13px \"Segoe UI\";");

        languageComboBox.getSelectionModel().selectedItemProperty().addListener((observableValue, oldValue, newValue) -> {
            Locale locale = LANGUAGE_MAP.get(newValue);
            ResourceBundle bundle = ResourceBundle.getBundle("Messages", locale); // 修复资源包名称
            localizator.setBundle(bundle);
            AuthProvider.setCurrentLanguage(newValue);
            changeLanguage();
        });
        loginField.textProperty().addListener((observableValue, oldValue, newValue) -> {
            if (newValue == null || !newValue.matches(".{0,40}")) {
                loginField.setText(oldValue);
            }
        });
        passwordField.textProperty().addListener((observableValue, oldValue, newValue) -> {
            if (newValue == null || !newValue.matches("\\S+")) {
                passwordField.setText(oldValue);
            }
        });
        submitButton.setOnAction(e -> {
            try {
                handleAuth();
            } catch (NetworkException ex) {
                throw new RuntimeException(ex);
            }
        });
    }

    /**
     * 实现用户登录和注册功能
     */
    @FXML
    private void handleAuth() throws NetworkException {
        String username = loginField.getText();
        String password = passwordField.getText();

        CommandRequest request = new CommandRequest(registerButton.isSelected() ? CommandType.REGISTER : CommandType.LOGIN);
        request.addArgument("username", username)
                .addArgument("password", password);
        try {
            CommandResponse response = proxy.sendRequest(request);
            if (response.isSuccess()) {
                User user = (User) response.getData();
                if (user != null) {
                    AuthProvider.setCurrentUser(user);
                    // 手动触发数据刷新
                    CommandRequest refreshRequest = new CommandRequest(CommandType.REFRESH);
                    CommandResponse refreshResponse = proxy.sendRequest(refreshRequest);
                    if (refreshResponse.isSuccess()) {
                        List<Product> products = (List<Product>) refreshResponse.getData();
                        // 更新界面数据（假设有回调方法）
                        Platform.runLater(() -> {
                            callback.run();
                            // 通知主界面更新数据
                            Event.publish(new DataUpdateEvent(products));
                        });
                    }
                } else {
                    showErrorDialog("Invalid user data");
                }
            } else {
                showErrorDialog(response.getMessage());
            }
        } catch (NetworkException e) {
            e.printStackTrace();
            showErrorDialog("Network Error: " + e.getMessage());
        }catch (Exception e) {
            e.printStackTrace();
            showErrorDialog("Unexpected Error: " + e.getMessage());
        }
    }

    private void showErrorDialog(String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setContentText(message);
        alert.show();
    }

    public void changeLanguage() {
        titleLabel.setText(LocalizationManager.getString("AuthTitle"));
        loginField.setPromptText(LocalizationManager.getString("LoginField"));
        passwordField.setPromptText(LocalizationManager.getString("PasswordField"));
        registerButton.setText(LocalizationManager.getString("RegisterButton"));
        submitButton.setText(LocalizationManager.getString("Submit"));
    }
    public void setCallback(Runnable callback) {
        this.callback = callback;
    }

    public void setClient(ServerProxy proxy) {
        this.proxy = proxy;
    }

    public void setLocalizator(LocalizationManager localizator) {
        this.localizator = localizator;
    }
}
