package command;

import exception.EmptyInputException;
import exception.NetworkException;
import model.Product;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class AddIfMinCommand implements Command {
    private final ServerProxy proxy;

    public AddIfMinCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please log in first!");
            return;
        }

        try {
            Product product = new Product();
            System.out.print("Enter the product name: ");
            product.setName(scanner.nextLine());

            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.ADD_IF_MIN)
                    .addArgument("product", product);

            CommandResponse response = proxy.sendRequest(request);
            System.out.println(response.getMessage());
            SessionState.refresh();
        } catch (Exception | EmptyInputException | NetworkException e) {
            System.err.println("Failed to add: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию, если его значение меньше, чем у наименьшего элемента этой коллекции";
    }

    @Override
    public String getName() {
        return "add_if_min";
    }
}