package server.command;

import client.command.ExecutableCommand;
import model.Product;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

import java.util.Optional;

public class AddIfMin implements ExecutableCommand {
    private Product newProduct;
    private final CollectionManager manager;

    public AddIfMin(CollectionManager manager) {
        this.manager = manager;
    }

    public void setNewProduct(Product newProduct) {
        this.newProduct = newProduct;
    }

    public Product getNewProduct() {
        return newProduct;
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию, если его значение меньше, чем у наименьшего элемента этой коллекции";
    }

    @Override
    public String getName() {
        return "add_if_min";
    }

    @Override
    public String execute() {
        try {
            Optional<Product> minProduct = manager.getCollection().stream().min(Product::compareTo);

            if (minProduct.isEmpty() || newProduct.compareTo(minProduct.get()) < 0) {
                manager.addProduct(newProduct);
                ServerLogger.logInfo("Product added (minimization condition satisfied), ID: " + newProduct.getId());
            } else {
                ServerLogger.logInfo("Product not added (does not satisfy min condition)");
            }
        } catch (Exception e) {
            ServerLogger.logError("Failed to execute command 'add_if_min'.", e);
        }
        return null;
    }
}
