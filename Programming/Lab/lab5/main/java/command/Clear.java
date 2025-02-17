package command;

import manager.CollectionManager;
import util.InputHandler;

public class Clear implements Command {
    private final CollectionManager manager;

    public Clear(CollectionManager manager, InputHandler inputHandler) {
        this.manager = manager;
    }


    @Override
    public void execute(String[] args) {
        manager.clearCollection();
        manager.getConsole().printSuccess("The collection has been emptied");
    }

    @Override
    public String getDescription() {
        return "очистить коллекцию";
    }

    @Override
    public String getName() {
        return "clear";
    }
}
