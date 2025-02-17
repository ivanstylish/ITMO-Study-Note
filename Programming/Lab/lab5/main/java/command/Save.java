package command;

import manager.CollectionManager;

public class Save implements Command {
    private final CollectionManager manager;

    public Save(CollectionManager manager) {
        this.manager = manager;
    }

    @Override
    public void execute(String[] args) {
        manager.saveToFile();
        manager.getConsole().printSuccess("The collection has been saved successfully");
    }

    @Override
    public String getDescription() {
        return "сохранить коллекцию в файл";
    }

    @Override
    public String getName() {
        return "save";
    }
}
