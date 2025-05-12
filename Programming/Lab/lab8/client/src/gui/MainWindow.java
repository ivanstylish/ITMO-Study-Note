package gui;

import controller.MainController;
import javafx.application.Platform;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.stage.Stage;
import network.ServerProxy;
import network.RealTimeSyncHandler;
import util.DataUpdateEvent;
import util.Event;

import java.util.HashMap;
import java.util.Map;


public class MainWindow extends Stage {
    private final MainController controller;
    private final ServerProxy serverProxy;
    private final TablePanel tablePanel = new TablePanel();
    private final VisualizationPanel visualizationPanel = new VisualizationPanel();
    private final TabPane tabPane = new TabPane();

    public Button addButton = new Button();
    public Button removeByIdButton = new Button();
    public Button updateButton = new Button();
    public Button addIfMinButton = new Button();
    public Button clearButton = new Button();
    public Button refreshButton = new Button();
    public Button countByUnitOfMeasureButton = new Button();
    public Button maxByCreationDateButton = new Button();
    public Button insertAtButton = new Button();
    public Button removeAnyByPriceButton = new Button();
    public Button showButton = new Button();
    public Button sortButton = new Button();
    public Button logoutButton = new Button();
    public Button exitButton = new Button();
    public Button executeScriptButton = new Button();
    public Button infoButton = new Button();
    public Button helpButton = new Button();
    public MainWindow(ServerProxy serverProxy, MainController controller) {
        this.serverProxy = serverProxy;
        this.controller = controller;
        initUI();
        initSync();
        initEventForwarding();
    }

    private void initEventForwarding() {
        Map<Button, String> buttonCommands = new HashMap<>();
        buttonCommands.put(addButton, "Add");
        buttonCommands.put(removeByIdButton, "RemoveByID");
        buttonCommands.put(updateButton, "Update");
        buttonCommands.put(addIfMinButton, "AddIfMin");
        buttonCommands.put(clearButton, "Clear");
        buttonCommands.put(refreshButton, "Refresh");
        buttonCommands.put(logoutButton, "LogOut");
        buttonCommands.put(showButton, "Show");
        buttonCommands.put(sortButton, "Sort");
        buttonCommands.put(removeAnyByPriceButton, "RemoveAnyByPrice");
        buttonCommands.put(exitButton, "Exit");
        buttonCommands.put(executeScriptButton, "ExecuteScript");
        buttonCommands.put(helpButton, "Help");
        buttonCommands.put(infoButton, "Info");
        buttonCommands.put(insertAtButton, "InsertAt");
        buttonCommands.put(countByUnitOfMeasureButton, "CountByUnitOfMeasure");
        buttonCommands.put(maxByCreationDateButton, "MaxByCreationDate");

        buttonCommands.forEach((button, cmd) -> button.setOnAction(e -> controller.handleButtonAction(cmd)));
    }

    private void initUI() {
        BorderPane root = new BorderPane();

        // 顶部工具栏（语言切换）
        LanguageSwitcher languageSwitcher = new LanguageSwitcher();
        root.setTop(languageSwitcher);

        // 选项卡
        Tab tableTab = new Tab("Table", tablePanel);
        Tab visualTab = new Tab("Visual", visualizationPanel);
        tabPane.getTabs().addAll(tableTab, visualTab);
        root.setCenter(tabPane);

        // 命令按钮面板
        GridPane buttonPanel = new GridPane();
        // 添加按钮（参考原 MainWindow 的 addCommandButtons()）
        root.setBottom(buttonPanel);

        Scene scene = new Scene(root, 800, 600);
        this.setScene(scene);
        this.setTitle("Product Management System");
    }

    private void initSync() {
        // 触发数据刷新
        new RealTimeSyncHandler(serverProxy, controller::refreshData);

        Event.subscribe(DataUpdateEvent.class, event -> Platform.runLater(() -> {
            visualizationPanel.updateProducts(event.getProducts());
            tablePanel.updateData(event.getProducts()); // 更新表格
        }));
    }
}