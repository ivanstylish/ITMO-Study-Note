package command;

import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class RemoveByIdCommand implements Command {
    private final ServerProxy proxy;


    public RemoveByIdCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please log in first!");
        }
        try {
            long id = Long.parseLong(parts[1]);
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.REMOVE_BY_ID)
                    .addArgument("id", id);
            CommandResponse response = proxy.sendRequest(request);
            System.out.println(response.getMessage());
        } catch (Exception | NetworkException e) {
            System.err.println("Failed to delete: " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    @Override
    public String getDescription() {
        return "удалить из коллекции один элемент, значение поля price которого эквивалентно заданному";
    }

    @Override
    public String getName() {
        return "remove_by_id";
    }
}
