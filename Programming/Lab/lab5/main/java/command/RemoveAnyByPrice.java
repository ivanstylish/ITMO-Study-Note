package command;

import manager.CollectionManager;

public class RemoveAnyByPrice implements Command {
    private final CollectionManager manager;

    public RemoveAnyByPrice(CollectionManager manager) {
        this.manager = manager;
    }

    @Override
    public void execute(String[] args) {
        if (args.length < 1) {
            manager.getConsole().printError("Need to provide ID parameter");
            return;
        }
        try {
            long id = Long.parseLong(args[0]);
            if (manager.removeAnyByPrice(id)) {
                manager.getConsole().printSuccess("Product deleted successfully");
            } else {
                manager.getConsole().printError("The product with the specified ID was not found");
            }
        } catch (NumberFormatException e) {
            manager.getConsole().printError("Invalid Id format");
        }
    }

    @Override
    public String getDescription() {
        return "удалить из коллекции один элемент, значение поля price которого эквивалентно заданному";
    }

    @Override
    public String getName() {
        return "remove_any_by_price";
    }
}
