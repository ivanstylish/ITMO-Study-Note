package command;

import exception.NetworkException;
import model.Product;
import network.ServerProxy;

import java.util.List;
import java.util.Scanner;

public class ShowCommand implements Command {
    private final ServerProxy proxy;

    public ShowCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        try {
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.SHOW);

            CommandResponse response = proxy.sendRequest(request);
            if (response.isSuccess()) {
                List<Product> products = (List<Product>) response.getData();
                if (products != null) {
                    products.forEach(System.out::println);
                } else {
                    System.out.println("No products found.");
                }
            } else {
                System.out.println("Error: " + response.getMessage());
            }
        } catch (Exception | NetworkException e) {
            System.err.println("Failed to show: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "вывести в стандартный поток вывода все элементы коллекции в строковом представлении";
    }

    @Override
    public String getName() {
        return "show";
    }
}
