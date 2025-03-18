package server.command;

import client.command.ExecutableCommand;
import model.Product;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class Update implements ExecutableCommand {
    private long id;
    private Product newProduct;
    private final CollectionManager collectionManager;

    public Update(CollectionManager collectionManager) {
        this.collectionManager = collectionManager;
    }

    public void setId(long id) {
        this.id = id;
    }

    public long getId() {
        return id;
    }

    public void setNewProduct(Product newProduct) {
        this.newProduct = newProduct;
    }

    public Product getNewProduct() {
        return newProduct;
    }

    @Override
    public String getDescription() {
        return "обновить значение элемента коллекции, id которого равен заданному";
    }

    @Override
    public String getName() {
        return "update";
    }

    @Override
    public String execute() {
        if (newProduct == null) {
            throw new IllegalArgumentException("Product cannot be null");
        }
        if (id <= 0) {
            throw new IllegalArgumentException("Invalid ID");
        }
        try {
            collectionManager.updateProduct(id, newProduct);
            ServerLogger.logInfo("Updated product with ID " + id);
        } catch (Exception e) {
            ServerLogger.logError("Failed to update product.", e);
        }
        return null;
    }
}
