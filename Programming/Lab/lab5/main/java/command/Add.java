package command;

import exception.InvalidInputException;
import manager.CollectionManager;
import model.Product;
import util.Console;
import util.InputHandler;


public class Add implements Command {
    private final CollectionManager collectionManager;
    private final Console console;

    public Add(CollectionManager collectionManager, Console console) {
        super();
        this.collectionManager = collectionManager;
        this.console = console;
    }


    @Override
    public void execute(String[] args) {
        if (args.length > 0) {
            collectionManager.getConsole().printError("This command does not accept arguments");
            return;
        }
        try {
            Product product = new InputHandler(collectionManager, console).inputProduct();
            // 调试输出
            System.out.println("[DEBUG] Product name: " + product.getName());
            collectionManager.addProduct(product);
        } catch (InvalidInputException e) {
            console.printError(e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию";
    }

    @Override
    public String getName() {
        return "add";
    }
}
