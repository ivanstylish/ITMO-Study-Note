package command;

import manager.CollectionManager;

public class Show implements Command {
    private final CollectionManager manager;

    public Show(CollectionManager manager) {
        this.manager = manager;
    }
    @Override
    public void execute(String[] args) {
        if (manager.getCollection().isEmpty()) {
            manager.getConsole().printInfo("Collection is empty");
        } else {
            manager.getCollection().forEach(element ->
                    manager.getConsole().printInfo(element.toString()));
        }
    }

    @Override
    public String getDescription() {
        return "вывести в стандартный поток вывода все элементы коллекции в строковом представлении";
    }

    @Override
    public String getName() {
        return "show";
    }
}
