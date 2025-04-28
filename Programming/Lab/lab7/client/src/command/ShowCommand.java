package command;

import dao.ProductDAO;
import exception.NetworkException;
import model.Product;
import network.ServerProxy;
import state.SessionState;

import java.util.List;
import java.util.Scanner;

public class ShowCommand implements Command {
    private final ServerProxy proxy;
    private final ProductDAO productDAO;

    public ShowCommand(ServerProxy proxy, ProductDAO productDAO) {
        this.proxy = proxy;
        this.productDAO = productDAO;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please login first.");
            return;
        }
        try {
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.SHOW);

            CommandResponse response = proxy.sendRequest(request);
            if (response.isSuccess()) {
                List<Product> products = productDAO.show();
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
