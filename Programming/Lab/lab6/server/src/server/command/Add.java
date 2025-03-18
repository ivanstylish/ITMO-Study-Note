package server.command;

import client.command.ExecutableCommand;
import model.Product;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

import java.io.Serial;

public class Add implements ExecutableCommand {
    @Serial
    private static final long serialVersionUID = 1L;
    private Product product;
    private transient CollectionManager collectionManager;

    public Add(CollectionManager collectionManager, Product product) {
        this.collectionManager = collectionManager;
        this.product = product;
    }

    public void setCollectionManager(CollectionManager manager) {
        this.collectionManager = manager;
    }
    public void setProduct(Product product) {
        this.product = product;
    }

    public Product getProduct() {
        return product;
    }

    @Override
    public String execute() {
        try {
            collectionManager.addProduct(product);
            String message = "Product added, ID: " + product.getId();
            ServerLogger.logInfo(message);
            return message;
        } catch (Exception e) {
            ServerLogger.logError("Failed to add: ", e);
            return "Error: " + e.getMessage();
        }
    }

    @Override
    public String getName() {
        return "add";
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию";
    }
}