package command;

import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.util.Map;
import java.util.Scanner;

public class HelpCommand implements Command {
    private final ServerProxy proxy;

    public HelpCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }


    @Override
    public void execute(String[] parts, Scanner scanner) {
        try {
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.HELP);

            CommandResponse response = proxy.sendRequest(request);

            if (response.isSuccess()) {
                System.out.println(response.getMessage());
            } else {
                System.out.println("Failed to get help: " + response.getMessage());
            }
            SessionState.refresh();
        } catch (NetworkException e) {
            System.err.println("Network error: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "вывести справку по доступным командам";
    }

    @Override
    public String getName() {
        return "help";
    }
}
