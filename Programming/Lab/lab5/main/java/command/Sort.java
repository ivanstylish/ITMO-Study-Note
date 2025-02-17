package command;

import manager.CollectionManager;

public class Sort implements Command {
    private final CollectionManager manager;

    public Sort(CollectionManager manager) {
        this.manager = manager;
    }


    @Override
    public void execute(String[] args) {
        manager.sortCollection();
        manager.getConsole().printSuccess("The collection is sorted");
    }

    @Override
    public String getDescription() {
        return "отсортировать коллекцию в естественном порядке";
    }

    @Override
    public String getName() {
        return "sort";
    }
}
