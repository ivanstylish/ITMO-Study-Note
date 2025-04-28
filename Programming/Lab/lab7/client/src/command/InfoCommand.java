package command;

import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class InfoCommand implements Command{
    private final ServerProxy proxy;

    public InfoCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please log in first!");
            return;
        }
        try {
            CommandRequest request = new CommandRequest().setCommandType(CommandType.INFO);
            CommandResponse response = proxy.sendRequest(request);
            System.out.println(response.getMessage());
        } catch (NetworkException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public String getDescription() {
        return "вывести в стандартный поток вывода информацию о коллекции";
    }

    @Override
    public String getName() {
        return "info";
    }
}
