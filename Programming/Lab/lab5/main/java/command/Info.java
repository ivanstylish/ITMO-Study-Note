package command;

import manager.CollectionManager;

public class Info implements Command {
    private final CollectionManager manager;

    public Info(CollectionManager manager) {
        this.manager = manager;
    }

    @Override
    public void execute(String[] args) {
        manager.getConsole().printInfo("Collection type: " + manager.getCollection().getClass().getSimpleName());
        manager.getConsole().printInfo("Number of elements: " + manager.getCollection().size());
    }

    @Override
    public String getDescription() {
        return "вывести в стандартный поток вывода информацию о коллекции";
    }

    @Override
    public String getName() {
        return "info";
    }
}
