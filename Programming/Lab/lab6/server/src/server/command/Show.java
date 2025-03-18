package server.command;


import client.command.ExecutableCommand;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class Show implements ExecutableCommand {
    private final CollectionManager collectionManager;

    public Show(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;
    }

    @Override
    public String getDescription() {
        return "вывести в стандартный поток вывода все элементы коллекции в строковом представлении";
    }

    @Override
    public String getName() {
        return "show";
    }

    @Override
    public String execute() {
        try {
            String collectionInfo = collectionManager.getCollection().toString();
            ServerLogger.logInfo("Current collection content: \n" + collectionInfo);
        } catch (Exception e) {
            ServerLogger.logError("Display collection failure", e);
        }
        return null;
    }
}
