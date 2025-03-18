package server.command;

import client.command.ExecutableCommand;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class Clear implements ExecutableCommand {
    private final CollectionManager manager;

    public Clear(CollectionManager manager) {
        this.manager = manager;
    }

    @Override
    public String getDescription() {
        return "очистить коллекцию";
    }

    @Override
    public String getName() {
        return "clear";
    }

    @Override
    public String execute() {
        try {
            manager.clearCollection();
        } catch (Exception e) {
            ServerLogger.logError("Failed to clear collection.", e);
        }
        return null;
    }
}
