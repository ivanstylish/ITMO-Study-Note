package command;

import exception.NetworkException;
import model.UnitOfMeasure;
import network.ServerProxy;
import state.SessionState;

import java.util.Scanner;

public class CountByUnitOfMeasureCommand implements Command {
    private final ServerProxy proxy;

    public CountByUnitOfMeasureCommand(ServerProxy proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please login first.");
            return;
        }
        System.out.print("Input unit type: ");
        String unit = scanner.nextLine().toUpperCase();

        try {
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.COUNT_BY_UNIT_OF_MEASURE)
                    .addArgument("unit", UnitOfMeasure.valueOf(unit));

            CommandResponse response = proxy.sendRequest(request);
            System.out.println("quantities: " + response.getIntegerArgument("count"));
        } catch (Exception | NetworkException e) {
            System.err.println("Failed to statistic: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "вывести количество элементов, значение поля unitOfMeasure которых равно заданному";
    }

    @Override
    public String getName() {
        return "count_by_unit_of_measure";
    }
}