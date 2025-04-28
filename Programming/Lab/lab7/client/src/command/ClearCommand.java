package command;

import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class ClearCommand implements Command {
    private final ServerProxy proxy;

    public ClearCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please log in first!");
            return;
        }

        try {
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.CLEAR);

            CommandResponse response = proxy.sendRequest(request);
            System.out.println(response.getMessage());
            SessionState.refresh();
        } catch (Exception | NetworkException e) {
            System.err.println("Failed to clear: " + e.getMessage());
        }
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