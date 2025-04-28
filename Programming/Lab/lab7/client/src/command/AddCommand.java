package command;

import exception.InvalidInputException;
import exception.NetworkException;
import exception.WrongLengthException;
import model.Product;
import model.User;
import network.ServerProxy;
import state.SessionState;
import ui.InputHandler;

import java.util.Scanner;

public class AddCommand implements Command {
    private final ServerProxy proxy;
    private final InputHandler inputHandler;

    public AddCommand(ServerProxy proxy, InputHandler inputHandler) {
        this.proxy = proxy;
        this.inputHandler = inputHandler;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please log in first!");
            return;
        }
        try {
            Product product = inputHandler.inputProduct();
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.ADD)
                    .addArgument("product", product)
                    .addArgument("userId", SessionState.getCurrentUser().getId());

            CommandResponse response = proxy.sendRequest(request);
            System.out.println(response.getMessage());
            SessionState.refresh();
        } catch (InvalidInputException | WrongLengthException | NetworkException e) {
            System.err.println("Failed to add: " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию";
    }

    @Override
    public String getName() {
        return "add";
    }

}