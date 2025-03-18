package server.command;


import client.command.ExecutableCommand;
import model.Product;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

import java.util.Optional;

public class MaxByCreationDate implements ExecutableCommand {
    private final CollectionManager collectionManager;

    public MaxByCreationDate(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;
    }

    @Override
    public String getDescription() {
        return "вывести любой объект из коллекции, значение поля creationDate которого является максимальным";
    }

    @Override
    public String getName() {
        return "max_by_creation_date";
    }

    @Override
    public String execute() {
        try {
            Optional<Product> product = collectionManager.getProductWithMaxDate();
            if (product.isPresent()) {
                ServerLogger.logInfo("New Products: " + product.get());
            } else {
                ServerLogger.logInfo("The collection is empty.");
            }
        } catch (Exception e) {
            ServerLogger.logError("Failed to find the latest product", e);
        }
        return null;
    }
}
