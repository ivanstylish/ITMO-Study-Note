package command;

import java.util.Scanner;

public class UpdateCommand implements Command {
    @Override
    public void execute(String[] parts, Scanner scanner) {

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
