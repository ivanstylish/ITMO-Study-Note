package command;

import exception.InvalidInputException;
import manager.CollectionManager;
import model.Product;
import util.InputHandler;

public class InsertAtIndex implements Command {
    private final CollectionManager manager;
    private final InputHandler inputHandler;

    public InsertAtIndex(CollectionManager manager, InputHandler inputHandler) {
        this.manager = manager;
        this.inputHandler = inputHandler;
    }

    @Override
    public void execute(String[] args) {
        if (args.length < 1) {
            manager.getConsole().printError("Need to provide index parameter");
            return;
        }

        try {
            int index = Integer.parseInt(args[0]);
            Product product = inputHandler.inputProduct();

            if (manager.insertProduct(index, product)) {
                manager.getConsole().printSuccess("Element inserted successfully");
            }else {
                manager.getConsole().printError("Invalid index location");
            }
        } catch (NumberFormatException e) {
            manager.getConsole().printError("Invalid index location");
        } catch (InvalidInputException e) {
            manager.getConsole().printError(e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в заданную позицию";
    }

    @Override
    public String getName() {
        return "insert_at";
    }
}
