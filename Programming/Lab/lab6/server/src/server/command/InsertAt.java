package server.command;

import client.command.ExecutableCommand;
import model.Product;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class InsertAt implements ExecutableCommand {
    private long index;
    private Product product;
    private final CollectionManager collectionManager;

    public InsertAt(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;
    }

    public Product getProduct() {
        return product;
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в заданную позицию";
    }

    @Override
    public String getName() {
        return "insert_at";
    }

    @Override
    public String execute() {
        try {
            boolean success = collectionManager.insertProduct((int)index, product);
            if (success) {
                ServerLogger.logInfo("Product inserted into the index " + index);
            } else {
                ServerLogger.logInfo("Insertion failure (index out of bounds)");
            }
        } catch (Exception e) {
            ServerLogger.logError("Failed to insert product.", e);
        }
        return null;
    }
}
