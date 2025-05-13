package controller;

import auth.AuthProvider;
import commandUtil.Command;
import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import commandUtil.CommandType;
import exception.NetworkException;
import gui.AuthWindow;
import gui.LanguageSwitcher;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.GridPane;
import javafx.stage.Stage;
import model.*;
import network.ServerProxy;
import user.User;
import util.DataUpdateEvent;
import util.Event;
import util.FileSelector;
import util.LocalizationManager;

import java.io.File;
import java.util.*;

public class MainController {
    private final Map<String, Command> commands = new HashMap<>();
    private final ServerProxy proxy;
    public TableView tableTable;
    public AnchorPane visualPane;

    @FXML
    private ComboBox<String> languageComboBox;
    @FXML
    private Label userLabel;
    @FXML
    private TableView<Product> productTable;
    @FXML
    private Button refreshButton;

    @FXML private Button helpButton;
    @FXML private Button infoButton;
    @FXML private Button addButton;
    @FXML private Button updateButton;
    @FXML private Button removeByIdButton;
    @FXML private Button addIfMinButton;
    @FXML private Button executeScriptButton;
    @FXML private Button exitButton;
    @FXML private Button clearButton;
    @FXML private Button countByUnitOfMeasureButton;
    @FXML private Button maxByCreationDateButton;
    @FXML private Button insertAtButton;
    @FXML private Button removeAnyByPriceButton;
    @FXML private Button showButton;
    @FXML private Button sortButton;
    @FXML private Button logoutButton;

    @FXML private Tab tableTab;

    @FXML private TableColumn<Product, String> userColumn;
    @FXML private TableColumn<Product, Integer> idColumn;
    @FXML private TableColumn<Product, String> nameColumn;
    @FXML private TableColumn<Product, Integer> xColumn;
    @FXML private TableColumn<Product, Long> yColumn;
    @FXML private TableColumn<Product, String> dateColumn;
    @FXML private TableColumn<Product, Long> priceColumn;
    @FXML private TableColumn<Product, String> unitOfMeasureColumn;

    @FXML private TableColumn<Product, Integer> organizationIdColumn;
    @FXML private TableColumn<Product, String> organizationNameColumn;
    @FXML private TableColumn<Product, String> organizationFullNameColumn;
    @FXML private TableColumn<Product, String> organizationTypeColumn;
    @FXML private Tab visualTab;


    public MainController(ServerProxy proxy) {
        this.proxy = proxy;
    }


    private void initLocales() {
        Map<String, Locale> locales = Map.of(
                "English (UK)", Locale.UK,
                "Русский", new Locale("ru"),
                "Македонски", new Locale("mk"),
                "Dansk", new Locale("da")
        );
        languageComboBox.getItems().addAll(locales.keySet());
        languageComboBox.getSelectionModel().selectedItemProperty().addListener(
                (obs, oldVal, newVal) -> updateLocale(locales.get(newVal))
        );
    }

    @FXML
    public void initialize() {
        setupTableColumns();
        initLocales();
        setupButtonActions();
        refreshData();
        updateUITexts();

        Event.subscribe(DataUpdateEvent.class, event ->
                Platform.runLater(this::refreshData)
        );
        Event.subscribe(LanguageSwitcher.class, event -> updateUITexts());
    }
    public void handleButtonAction(String command) {
        switch (command) {
            case "Add": handleAdd(); break;
            case "RemoveByID": handleRemoveById(); break;
            case "Update": handleUpdate(); break;
            case "AddIfMin": handleAddIfMin(); break;
            case "Clear": handleClear(); break;
            case "Refresh": refreshData(); break;
            case "LogOut": handleLogout(); break;
            case "Show": handleShow(); break;
            case "Sort": handleSort(); break;
            case "RemoveAnyByPrice": handleRemoveAnyByPrice(); break;
            case "Exit": handleExit(); break;
            case "ExecuteScript": handleExecuteScript(); break;
            case "Help": handleHelp(); break;
            case "Info": handleInfo(); break;
            case "InsertAt": handleInsertAt(); break;
        }
    }
    @FXML
    private void setupButtonActions() {
        helpButton.setOnAction(e -> handleHelp());
        infoButton.setOnAction(e -> handleInfo());
        addButton.setOnAction(e -> handleAdd());
        updateButton.setOnAction(e -> handleUpdate());
        removeByIdButton.setOnAction(e -> handleRemoveById());
        addIfMinButton.setOnAction(e -> handleAddIfMin());
        clearButton.setOnAction(e -> handleClear());
        countByUnitOfMeasureButton.setOnAction(e -> handleCountByUnitOfMeasure());
        maxByCreationDateButton.setOnAction(e -> handleMaxByCreationDate());
        insertAtButton.setOnAction(e -> handleInsertAt());
        removeAnyByPriceButton.setOnAction(e -> handleRemoveAnyByPrice());
        showButton.setOnAction(e -> handleShow());
        sortButton.setOnAction(e -> handleSort());
        logoutButton.setOnAction(e -> handleLogout());
        executeScriptButton.setOnAction(e -> handleExecuteScript());
        exitButton.setOnAction(e -> handleExit());
        refreshButton.setOnAction(e -> refreshData());
    }

    @FXML
    private void handleUpdate() {
        TextInputDialog idDialog = new TextInputDialog();
        idDialog.setHeaderText(LocalizationManager.getString("EnterProductID"));
        Optional<String> idResult = idDialog.showAndWait();

        idResult.ifPresent(id -> {
            Dialog<Product> updateDialog = createProductDialog();
            Optional<Product> productResult = updateDialog.showAndWait();
            productResult.ifPresent(product -> {
                CommandRequest request = new CommandRequest(CommandType.UPDATE)
                        .addArgument("id", id)
                        .addArgument("product", product);
                executeRequest(request);
            });
        });
    }


    // Exit 退出命令
    @FXML
    private void handleExit() {
        Platform.exit();
    }

    // ExecuteScript 执行脚本命令
    @FXML
    private void handleExecuteScript() {
        Stage currentStage = (Stage) executeScriptButton.getScene().getWindow();

        FileSelector fileChooser = new FileSelector();
        File file = fileChooser.showOpenDialog(currentStage); // 传递 Stage
        if (file != null) {
            CommandRequest request = new CommandRequest(CommandType.EXECUTE_SCRIPT)
                    .addArgument("scriptPath", file.getAbsolutePath());
            executeRequest(request);
        }
    }

    // add 添加命令
    @FXML
    private void handleAdd() {
        Dialog<Product> addDialog = createProductDialog();
        Optional<Product> result = addDialog.showAndWait();
        result.ifPresent(product -> {
            CommandRequest request = new CommandRequest(CommandType.ADD)
                    .addArgument("product", product);
            executeRequest(request);
        });
    }

    // sort 排序命令
    @FXML
    private void handleSort() {
        executeCommand(CommandType.SORT);
    }

    // show 展示所有可用命令
    @FXML
    private void handleShow() {
        executeCommand(CommandType.SHOW);
    }

    // removeanybyprice 根据价格大小删除产品命令
    @FXML
    private void handleRemoveAnyByPrice() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setHeaderText(LocalizationManager.getString("EnterPrice"));
        Optional<String> result = dialog.showAndWait();

        result.ifPresent(price -> {
            try {
                CommandRequest request = new CommandRequest(CommandType.REMOVE_ANY_BY_PRICE)
                        .addArgument("price", Long.parseLong(price));
                executeRequest(request);
            } catch (NumberFormatException e) {
                showError(LocalizationManager.getString("InvalidNumberFormat"));
            }
        });
    }

    //insert_at 根据索引定位
    @FXML
    private void handleInsertAt() {
        TextInputDialog indexDialog = new TextInputDialog();
        indexDialog.setHeaderText(LocalizationManager.getString("EnterIndex"));
        Optional<String> indexResult = indexDialog.showAndWait();

        indexResult.ifPresent(index -> {
            try {
                int idx = Integer.parseInt(index);
                Dialog<Product> productDialog = createProductDialog();
                Optional<Product> productResult = productDialog.showAndWait();

                productResult.ifPresent(product -> {
                    CommandRequest request = new CommandRequest(CommandType.INSERT_AT)
                            .addArgument("index", idx)
                            .addArgument("product", product);
                    executeRequest(request);
                });
            } catch (NumberFormatException e) {
                showError(LocalizationManager.getString("InvalidNumberFormat"));
            }
        });
    }

    // maxbycreationdate 制造最大时间
    @FXML
    private void handleMaxByCreationDate() {
        executeCommand(CommandType.MAX_BY_CREATION_DATE);
    }

    // countbyunitofmeasure 单位
    @FXML
    private void handleCountByUnitOfMeasure() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setHeaderText("Enter Unit of Measure");
        Optional<String> result = dialog.showAndWait();
        result.ifPresent(unit -> {
            CommandRequest request = new CommandRequest(CommandType.COUNT_BY_UNIT_OF_MEASURE)
                    .addArgument("unit", unit);
            executeRequest(request);
        });
    }

    // addifmin 比大小
    @FXML
    private void handleAddIfMin() {
        Dialog<Product> dialog = createProductDialog();
        Optional<Product> result = dialog.showAndWait();
        result.ifPresent(product -> {
            CommandRequest request = new CommandRequest(CommandType.ADD_IF_MIN)
                    .addArgument("product", product);
            executeRequest(request);
        });
    }

    // info 查看集合信息
    @FXML
    private void handleInfo() {
        new Thread(() -> {
            try {
                CommandResponse response = proxy.sendRequest(new CommandRequest(CommandType.INFO));
                Platform.runLater(() -> {
                    if (response.isSuccess()) {
                        Map<String, Object> data = (Map<String, Object>) response.getData();
                        String info = String.format(
                                LocalizationManager.getString("InfoResult"),
                                data.getOrDefault("type", "N/A"),
                                data.getOrDefault("size", 0),
                                data.getOrDefault("initDate", "N/A"),
                                data.getOrDefault("updateDate", "N/A")
                        );
                        showInfo(info);
                    } else {
                        showError(response.getMessage());
                    }
                });
            } catch (NetworkException e) {
                Platform.runLater(() -> showError("Network Error: " + e.getMessage()));
            }
        }).start();
    }

    @FXML
    private void handleLogout() {
        try {
            CommandRequest request = new CommandRequest(CommandType.LOGOUT);
            request.setUser(AuthProvider.getCurrentUser());
            CommandResponse response = proxy.sendRequest(request);
            if (response.isSuccess()) {
                AuthProvider.setCurrentUser(null); // 清除用户信息
                Platform.runLater(() -> {
                    // 跳转回登录界面（假设存在 AuthWindow 类）
                    AuthWindow authWindow = new AuthWindow(proxy);
                    authWindow.show();
                    // 关闭当前窗口
                    ((Stage) logoutButton.getScene().getWindow()).close();
                });
            } else {
                showError(response.getMessage());
            }
        } catch (NetworkException e) {
            showError("Network Error: " + e.getMessage());
        }
    }

    @FXML
    public void handleRemoveById() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setHeaderText(LocalizationManager.getString("EnterProductID"));
        Optional<String> result = dialog.showAndWait();

        result.ifPresent(id -> {
            CommandRequest request = new CommandRequest(CommandType.REMOVE_BY_ID)
                    .addArgument("id", id);
            executeRequest(request);
        });
    }

    @FXML
    private void handleClear() {
        CommandRequest request = new CommandRequest(CommandType.CLEAR);
        CommandResponse response;
        try {
            response = proxy.sendRequest(request);
        } catch (NetworkException e) {
            throw new RuntimeException(e);
        }
        handleResponse(response);
    }

    @FXML
    private void handleHelp() {
        String helpText = LocalizationManager.getString("HelpResult");
        TextArea textArea = new TextArea(helpText);
        textArea.setEditable(false);

        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(LocalizationManager.getString("Help"));
        alert.getDialogPane().setContent(textArea);
        alert.showAndWait();
    }
    private void executeCommand(CommandType commandType) {
        Command command = commands.get(commandType);
        if (command != null) {
            new Thread(() -> {
                try {
                    CommandRequest request = new CommandRequest(commandType);
                    request.setUser(AuthProvider.getCurrentUser());

                    CommandResponse response = proxy.sendRequest(request);
                    Platform.runLater(() -> handleResponse(response));
                } catch (NetworkException e) {
                    Platform.runLater(() -> showError("Network Error: " + e.getMessage()));
                }
            }).start();
        }
    }
    private void executeRequest(CommandRequest request) {
        request.setUser(AuthProvider.getCurrentUser()); // 设置当前用户

        new Thread(() -> {
            try {
                CommandResponse response = proxy.sendRequest(request);
                Platform.runLater(() -> {
                    if (response.isSuccess()) {
                        handleResponse(response);
                    } else {
                        showError(response.getMessage());
                    }
                });
            } catch (NetworkException e) {
                Platform.runLater(() -> showError("Network Error: " + e.getMessage()));
            }
        }).start();
    }

    private void handleResponse(CommandResponse response) {
        if (response.isSuccess()) {
            showSuccess(response.getMessage());
        } else {
            showError(response.getMessage());
        }
    }

    @FXML
    public void refreshData() {
        new Thread(() -> {
            try {
                CommandResponse response = proxy.sendRequest(new CommandRequest(CommandType.GET_ALL));
                if (response.isSuccess()) {
                    List<Product> products = (List<Product>) response.getData();
                    Platform.runLater(() -> {
                        productTable.getItems().setAll(products);
                        // 通知可视化面板更新
                        Event.publish(new DataUpdateEvent(products));
                    });
                }
            } catch (NetworkException e) {
                Platform.runLater(() -> showError("Refresh failed: " + e.getMessage()));
            }
        }).start();
    }

    private Dialog<Product> createProductDialog() {
        Dialog<Product> dialog = new Dialog<>();
        dialog.setTitle(LocalizationManager.getString("AddProduct"));

        // 创建表单字段
        TextField nameField = new TextField();
        TextField priceField = new TextField();
        TextField xField = new TextField();
        TextField yField = new TextField();
        TextField org_nameField = new TextField();
        TextField org_fullnameField = new TextField();
        ComboBox<String> org_typeField = new ComboBox<>();
        ComboBox<String> unitCombo = new ComboBox<>();

        GridPane grid = new GridPane();
        grid.add(new Label(LocalizationManager.getString("Name")), 0, 0);
        grid.add(nameField, 1, 0);
        grid.add(new Label(LocalizationManager.getString("Price")), 0, 1);
        grid.add(priceField, 1, 1);
        grid.add(new Label("X Coordinate"), 0, 2);
        grid.add(xField, 1, 2);
        grid.add(new Label("Y Coordinate"), 0, 3);
        grid.add(yField, 1, 3);
        grid.add(new Label(LocalizationManager.getString("OrganizationName")), 0, 4);
        grid.add(org_nameField, 1, 4);
        grid.add(new Label(LocalizationManager.getString("OrganizationFullName")), 0, 5);
        grid.add(org_fullnameField, 1, 5);
        grid.add(new Label(LocalizationManager.getString("OrganizationType")), 0, 6);
        grid.add(org_typeField, 1, 6);
        grid.add(new Label(LocalizationManager.getString("UnitOfMeasure")), 0, 7);
        grid.add(unitCombo, 1, 7);

        dialog.getDialogPane().setContent(grid);
        dialog.getDialogPane().getButtonTypes().addAll(ButtonType.OK, ButtonType.CANCEL);

        // 结果转换器
        dialog.setResultConverter(buttonType -> {
            if (buttonType == ButtonType.OK) {
                try {
                    // 创建Coordinates和Organization对象
                    Coordinates coordinates = new Coordinates(
                            Integer.parseInt(xField.getText()),
                            Long.parseLong(yField.getText())
                    );
                    Organization organization = new Organization(
                            org_nameField.getText(),
                            org_fullnameField.getText(),
                            OrganizationType.valueOf(org_typeField.getValue())
                    );

                    return new Product(
                            null, // id由服务器生成
                            nameField.getText(),
                            coordinates,
                            Long.parseLong(priceField.getText()),
                            UnitOfMeasure.valueOf(unitCombo.getValue()),
                            organization
                    );
                } catch (Exception e) {
                    showError("Invalid input: " + e.getMessage());
                    return null;
                }
            }
            return null;
        });

        return dialog;
    }

    private void updateUITexts() {
        User currentUser = AuthProvider.getCurrentUser();
        if (currentUser != null) {
            userLabel.setText(LocalizationManager.getString("User") + ": " + currentUser.getUsername());
        } else {
            userLabel.setText(LocalizationManager.getString("User") + ": " + "not logged in");
        }
        Platform.runLater(() -> {
            AuthWindow authWindow = new AuthWindow(proxy);
            authWindow.show();
            ((Stage) userLabel.getScene().getWindow()).close();
        });
        // 命令按钮
        helpButton.setText(LocalizationManager.getString("Help"));
        addButton.setText(LocalizationManager.getString("Add"));
        removeByIdButton.setText(LocalizationManager.getString("RemoveByID"));
        clearButton.setText(LocalizationManager.getString("Clear"));
        helpButton.setText(LocalizationManager.getString("Help"));
        addIfMinButton.setText(LocalizationManager.getString("AddIfMin"));
        countByUnitOfMeasureButton.setText(LocalizationManager.getString("CountByUnitOfMeasure"));
        executeScriptButton.setText(LocalizationManager.getString("ExecuteScript"));
        infoButton.setText(LocalizationManager.getString("Info"));
        insertAtButton.setText(LocalizationManager.getString("InsertAt"));
        maxByCreationDateButton.setText(LocalizationManager.getString("MaxByCreationDate"));
        removeAnyByPriceButton.setText(LocalizationManager.getString("RemoveAnyByPrice"));
        exitButton.setText(LocalizationManager.getString("Exit"));
        showButton.setText(LocalizationManager.getString("Show"));
        sortButton.setText(LocalizationManager.getString("Sort"));
        updateButton.setText(LocalizationManager.getString("Update"));
        logoutButton.setText(LocalizationManager.getString("LogOut"));
        refreshButton.setText(LocalizationManager.getString("Refresh"));

        tableTab.setText(LocalizationManager.getString("TableTab"));
        visualTab.setText(LocalizationManager.getString("VisualTab"));

        // 产品
        userColumn.setText(LocalizationManager.getString("User"));
        nameColumn.setText(LocalizationManager.getString("Name"));
        dateColumn.setText(LocalizationManager.getString("CreationDate"));
        priceColumn.setText(LocalizationManager.getString("Price"));
        unitOfMeasureColumn.setText(LocalizationManager.getString("UnitOfMeasure"));

        // 制造商
        organizationIdColumn.setText(LocalizationManager.getString("OrganizationId"));
        organizationNameColumn.setText(LocalizationManager.getString("OrganizationName"));
        organizationFullNameColumn.setText(LocalizationManager.getString("OrganizationFullName"));
        organizationTypeColumn.setText(LocalizationManager.getString("OrganizationType"));
    }

    private void updateLocale(Locale locale) {
        LocalizationManager.setLocale(locale);
        updateUITexts();
    }

    @FXML
    private void setupTableColumns() {
        Objects.requireNonNull(userColumn, "userColumn is not injected from FXML!");
        userColumn.setCellValueFactory(new PropertyValueFactory<>("User"));
        idColumn.setCellValueFactory(new PropertyValueFactory<>("Id"));
        nameColumn.setCellValueFactory(new PropertyValueFactory<>("Name"));
        xColumn.setCellValueFactory(new PropertyValueFactory<>("x"));
        yColumn.setCellValueFactory(new PropertyValueFactory<>("y"));
        dateColumn.setCellValueFactory(new PropertyValueFactory<>("creationDate"));
        priceColumn.setCellValueFactory(new PropertyValueFactory<>("price"));
        unitOfMeasureColumn.setCellValueFactory(new PropertyValueFactory<>("unitOfMeasure"));
        organizationIdColumn.setCellValueFactory(new PropertyValueFactory<>("organizationId"));
        organizationNameColumn.setCellValueFactory(new PropertyValueFactory<>("organizationName"));
        organizationFullNameColumn.setCellValueFactory(new PropertyValueFactory<>("organizationFullName"));
        organizationTypeColumn.setCellValueFactory(new PropertyValueFactory<>("organizationType"));
    }

    private void showError(String s) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setContentText(s);
        alert.show();
    }
    private void showSuccess(String s) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setContentText(s);
        alert.show();
    }
    private void showInfo(String message) {
        TextArea area = new TextArea(message);
        area.setEditable(false);
        new Alert(Alert.AlertType.INFORMATION).show();
    }
}

