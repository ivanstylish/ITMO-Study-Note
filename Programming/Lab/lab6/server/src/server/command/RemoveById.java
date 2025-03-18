package server.command;


import client.command.ExecutableCommand;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class RemoveById implements ExecutableCommand {
    private long id;
    private final CollectionManager collectionManager;

    public RemoveById(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;
    }

    public void setId(long id) {
        this.id = id;
    }

    public long getId() {
        return id;
    }

    @Override
    public String getDescription() {
        return "удалить элемент из коллекции по его id";
    }

    @Override
    public String getName() {
        return "remove_by_id";
    }

    @Override
    public String execute() {
        try {
            collectionManager.removeProductByID(id);
        } catch (Exception e) {
            ServerLogger.logError("Failed to delete product.", e);
        }
        return null;
    }
}
