package controller;

import auth.AuthProvider;
import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import commandUtil.CommandType;
import exception.NetworkException;
import javafx.collections.FXCollections;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import network.ServerProxy;
import user.User;
import util.LocalizationManager;

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
            if (!newValue.matches(".{0,40}")) {
                loginField.setText(oldValue);
            }
        });
        passwordField.textProperty().addListener((observableValue, oldValue, newValue) -> {
            if (!newValue.matches("\\S*")) {
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
    private void handleAuth() throws NetworkException {
        String username = loginField.getText();
        String password = passwordField.getText();

        CommandRequest request = new CommandRequest(registerButton.isSelected() ? CommandType.REGISTER : CommandType.LOGIN);
        request.addArgument("Username", username)
                .addArgument("Password", password);
        try{
            CommandResponse response = proxy.sendRequest(request);
            if (response.isSuccess()) {
                User user = (User) response.getData();
                AuthProvider.setCurrentUser(user);
                callback.run(); // 跳转到主程序
            } else {
                showErrorDialog(response.getMessage());
            }
        } catch (NetworkException e) {
            showErrorDialog("Network Error: " + e.getMessage());
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
