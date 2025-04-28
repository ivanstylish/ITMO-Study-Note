package command;

import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class RemoveAnyByPriceCommand implements Command {
    private final ServerProxy proxy;

    public RemoveAnyByPriceCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please login first.");
            return;
        }
        System.out.print("Input Price: ");
        long price = Long.parseLong(scanner.nextLine());

        try {
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.REMOVE_ANY_BY_PRICE)
                    .addArgument("price", price);

            CommandResponse response = proxy.sendRequest(request);
            System.out.println(response.getMessage());
        } catch (Exception | NetworkException e) {
            System.err.println("Failed to delete: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "удалить из коллекции один элемент, значение поля price которого эквивалентно заданному";
    }

    @Override
    public String getName() {
        return "remove_any_by_price";
    }
}