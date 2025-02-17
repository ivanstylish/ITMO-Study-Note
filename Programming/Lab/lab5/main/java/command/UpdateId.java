package command;

import exception.InvalidInputException;
import manager.CollectionManager;
import model.Product;
import util.InputHandler;

import java.util.Optional;

public class UpdateId implements Command {
    private final CollectionManager manager;
    private final InputHandler inputHandler;

    public UpdateId(CollectionManager manager, InputHandler inputHandler) {
        this.manager = manager;
        this.inputHandler = inputHandler;
    }

    @Override
    public void execute(String[] args) {
        if (args.length < 1) {
            manager.getConsole().printError("Need to provide ID parameter");
            return;
        }
        try {
            long id = Long.parseLong(args[0]);
            Optional<Product> product = manager.getProductById(id);
            if (product.isPresent()) {
                Product updatedId = inputHandler.inputProduct();
                manager.updateProduct(id, updatedId);
                manager.getConsole().printSuccess("Product update success");
            }else {
                manager.getConsole().printError("The product with the specified ID was not found");
            }
        }catch (NumberFormatException e) {
            manager.getConsole().printError("Invalid ID format");
        }catch (InvalidInputException e) {
            manager.getConsole().printError(e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "обновить значение элемента коллекции, id которого равен заданному";
    }

    @Override
    public String getName() {
        return "update";
    }
}
