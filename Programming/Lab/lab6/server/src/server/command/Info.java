package server.command;

import client.command.ExecutableCommand;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class Info implements ExecutableCommand {
    private final CollectionManager collectionManager;

    public Info(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;
    }
    @Override
    public String getDescription() {
        return "вывести в стандартный поток вывода информацию о коллекции (тип, дата инициализации, количество элементов и т.д.)";
    }

    @Override
    public String getName() {
        return "info";
    }

    @Override
    public String execute() {
        try {
            String info = "Collection type: Stack<Product>, size: " + collectionManager.getCollection().size();
            ServerLogger.logInfo(info);
        } catch (Exception e) {
            ServerLogger.logError("Failed to get collection information", e);
        }
        return null;
    }
}
