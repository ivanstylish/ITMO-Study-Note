package command;

import manager.CollectionManager;

public class RemoveById implements Command {
    private final CollectionManager manager;

    public RemoveById(CollectionManager manager) {
        this.manager = manager;
    }

    @Override
    public void execute(String[] args) {
        if (args.length < 1) {
            manager.getConsole().printError("ID parameter required");
            return;
        }

        try {
            long id = Long.parseLong(args[0]);
            if (manager.removeProductByID(id)) {
                manager.getConsole().printSuccess("Product deleted successfully");
            } else {
                manager.getConsole().printError("The product with the specified ID was not found");
            }
        } catch (NumberFormatException e) {
            manager.getConsole().printError("Invalid ID format");
        }
    }

    @Override
    public String getName() { return "remove_by_id"; }

    @Override
    public String getDescription() {
        return "удалить элемент из коллекции по его id";
    }
}
