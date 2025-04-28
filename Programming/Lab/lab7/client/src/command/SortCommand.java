package command;

import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class SortCommand implements Command {
    private final ServerProxy proxy;

    public SortCommand(ServerProxy proxy) {
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
                    .setCommandType(CommandType.SORT);

            CommandResponse response = proxy.sendRequest(request);
            System.out.println("The set is sorted: " + response.getMessage());
        } catch (Exception | NetworkException e) {
            System.err.println("Failed to sort: " + e.getMessage());
        }
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