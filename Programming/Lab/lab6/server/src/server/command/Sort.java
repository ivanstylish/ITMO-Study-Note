package server.command;

import client.command.ExecutableCommand;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class Sort implements ExecutableCommand {
    private final CollectionManager collectionManager;

    public Sort(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;

    }

    @Override
    public String getDescription() {
        return "отсортировать коллекцию в естественном порядке";
    }

    @Override
    public String getName() {
        return "sort";
    }

    @Override
    public String execute() {
        try {
            collectionManager.sortCollection();
            ServerLogger.logInfo("Collection sorted.");
        } catch (Exception e) {
            ServerLogger.logError("Failed to sort collection.", e);
        }
        return null;
    }
}
