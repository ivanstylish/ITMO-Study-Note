package command;


import java.util.Scanner;

public class ExitCommand implements Command {
    @Override
    public void execute(String[] parts, Scanner scanner) {
        System.out.println("EXIT...");
        System.out.println("\uD83D\uDE2D" + "\uD83D\uDE2D" + "\uD83D\uDE2D");
        System.out.println("._.");
        System.exit(0);
    }

    @Override
    public String getDescription() {
        return "завершить программу";
    }

    @Override
    public String getName() {
        return "exit";
    }
}