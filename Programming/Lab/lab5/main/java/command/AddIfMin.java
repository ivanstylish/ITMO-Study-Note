package command;

import exception.InvalidInputException;
import manager.CollectionManager;
import model.Product;
import util.InputHandler;

import java.util.Optional;

public class AddIfMin implements Command {
    private final CollectionManager collectionManager;
    private final InputHandler inputHandler;

    public AddIfMin(CollectionManager collectionManager, InputHandler inputHandler) {
        this.collectionManager = collectionManager;
        this.inputHandler = inputHandler;
    }


    @Override
    public void execute(String[] args) {
        try {
            Product newProduct = inputHandler.inputProduct();
            Optional<Product> minProduct = collectionManager.findMinProduct();
            if (minProduct.isEmpty() || newProduct.compareTo(minProduct.get()) < 0) {
                collectionManager.getConsole().printError("The product does not meet the minimum conditions.");
            }
        }catch (InvalidInputException e) {
            collectionManager.getConsole().printError(e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию, если его значение меньше, чем у наименьшего элемента этой коллекции";
    }

    @Override
    public String getName() {
        return "add_if_min";
    }
}
