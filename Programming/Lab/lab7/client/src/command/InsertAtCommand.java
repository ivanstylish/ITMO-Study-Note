package command;

import exception.NetworkException;
import model.UnitOfMeasure;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class InsertAtCommand implements Command{
    private final ServerProxy proxy;

    public InsertAtCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }
    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please login first.");
            return;
        }

        try {
            System.out.print("Enter insertion index: ");
            int index = Integer.parseInt(scanner.nextLine());

            System.out.print("Product name: ");
            String productName = scanner.nextLine().trim();

            System.out.print("Product price: ");
            long price = Long.parseLong(scanner.nextLine());

            System.out.print("Unit of measure (KILOGRAMS/SQUARE_METERS/LITERS/MILLILITERS/GRAMS): ".toUpperCase());
            UnitOfMeasure unit = UnitOfMeasure.valueOf(scanner.nextLine().toUpperCase());

            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.INSERT_AT)
                    .addArgument("index", index)
                    .addArgument("productName", productName)
                    .addArgument("price", price)
                    .addArgument("unitOfMeasure", unit);

            CommandResponse response = proxy.sendRequest(request);

            if (response.isSuccess()) {
                System.out.printf("Successfully inserted product at position %d%n", index);
                SessionState.refresh();
            } else {
                System.out.println("Insertion failed: " + response.getMessage());
            }

        } catch (NumberFormatException e) {
            System.err.println("Invalid numeric format: " + e.getMessage());
        } catch (IllegalArgumentException e) {
            System.err.println("Invalid unit of measure: " + e.getMessage());
            System.err.println("Valid values: KILOGRAMS, SQUARE_METERS, LITERS, MILLILITERS, GRAMS");
        } catch (NetworkException e) {
            System.err.println("Network error: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в заданную позицию";
    }

    @Override
    public String getName() {
        return "insert_at";
    }
}
