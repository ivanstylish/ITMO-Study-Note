package command;

import exception.InvalidInputException;
import exception.NetworkException;
import exception.WrongLengthException;
import model.Product;
import network.ServerProxy;
import state.SessionState;
import ui.InputHandler;

import java.util.Scanner;


public class UpdateCommand implements Command {
    private final ServerProxy proxy;
    private final InputHandler inputHandler;

    public UpdateCommand(ServerProxy proxy, InputHandler inputHandler) {
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
            long id = Long.parseLong(parts[1]);
            Product product = inputHandler.inputProduct();
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.UPDATE)
                    .addArgument("id", id)
                    .addArgument("product", product);

            CommandResponse response = proxy.sendRequest(request);
            System.out.println(response.getMessage());
            SessionState.refresh();
        } catch (InvalidInputException | WrongLengthException | NetworkException e) {
            System.err.println("Failed to update: " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    @Override
    public String getDescription() {
        return "обновить значение элемента коллекции, id которого равен заданному";
    }

    @Override
    public String getName() {
        return "update";
    }
}
