package server.command;

import client.command.BaseCommand;
import client.command.ExecutableCommand;
import model.Product;
import server.exception.CommandExecutionException;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;


public class ServerCommandExecutor {
    private final CollectionManager collectionManager;
    private final Product product;
    private final Map<String, ExecutableCommand> commandRegistry = new HashMap<>(); // 改为实例变量

    public ServerCommandExecutor(CollectionManager collectionManager, Product product) {
        this.collectionManager = collectionManager;
        this.product = product;
    }

    public void registerCommand(ExecutableCommand command) {
        commandRegistry.put(command.getName(), command);
    }

    // 改为实例方法
    public Object execute(BaseCommand command) throws CommandExecutionException {
        String commandName = command.getName();
        ServerLogger.logInfo("Execution of commands started: " + commandName);

        ExecutableCommand executableCommand = commandRegistry.get(commandName);
        if (executableCommand == null) {
            ServerLogger.logError("Command not registered: " + commandName, null);
            throw new CommandExecutionException("Invalid command: " + commandName);
        }
        ServerLogger.logCommand(commandName);

        try {
            String result = executableCommand.execute();
            return result != null ? result : "Command executed successfully";
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }
    public void showHelp() {
        String helpText = commandRegistry.values().stream()
                .map(cmd -> String.format("- %-20s: %s", cmd.getName(), cmd.getDescription()))
                .collect(Collectors.joining("\n"));
        ServerLogger.logInfo("List of available commands:\n" + helpText);
    }

    public CollectionManager getCollectionManager() {
        return collectionManager;
    }
    public Product getProduct() {
        return product;
    }
}
