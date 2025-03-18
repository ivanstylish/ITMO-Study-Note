package server.command;

import client.command.ExecutableCommand;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class RemoveAnyByPrice implements ExecutableCommand {
    private long price;
    private final CollectionManager collectionManager;

    public RemoveAnyByPrice(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;
    }

    @Override
    public String getDescription() {
        return "удалить из коллекции один элемент, значение поля price которого эквивалентно заданному";
    }

    @Override
    public String getName() {
        return "remove_any_by_price";
    }

    public long getPrice() {
        return price;
    }

    public void setPrice(long price) {
        this.price = price;
    }

    @Override
    public String execute() {
        try {
            collectionManager.removeAnyByPrice(price);
        } catch (Exception e) {
            ServerLogger.logError("Failed to delete.", e);
        }
        return null;
    }
}
