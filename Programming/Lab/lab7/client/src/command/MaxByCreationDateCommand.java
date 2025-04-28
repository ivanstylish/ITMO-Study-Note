package command;

import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class MaxByCreationDateCommand implements Command {
    private final ServerProxy proxy;

    public MaxByCreationDateCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please login first.");
            return;
        }
        try {
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.MAX_BY_CREATION_DATE);

            CommandResponse response = proxy.sendRequest(request);
            System.out.println("New Products: " + response.getStringArgument("maxProduct"));
        } catch (Exception | NetworkException e) {
            System.err.println("Failed to view: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "вывести любой объект из коллекции, значение поля creationDate которого является максимальным";
    }

    @Override
    public String getName() {
        return "max_by_creation_date";
    }
}