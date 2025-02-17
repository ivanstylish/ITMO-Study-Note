package command;
import util.Console;

import java.util.*;

public class CommandExecutor {
    private final Map<String, Command> commands = new HashMap<>();
    private final Console console;

    public CommandExecutor(Console console) {
        this.console = console;
    }

    public void registerCommand(Command command) {
        commands.put(command.getName().toLowerCase(), command);
    }

    public void execute(String input) {
        String[] parts = input.split("\\s+", 2);
        String commandName = parts[0].toLowerCase();

        if ("help".equals(commandName)) {
            showHelp();
            return;
        }

        Command cmd = commands.get(commandName);
        if (cmd != null) {
            try {
                String[] args = parts.length > 1 ? parseArguments(parts[1]) : new String[0];
                cmd.execute(args);
            } catch (Exception e) {
                console.printError("Implementation error: " + e.getMessage());
            }
        } else {
            console.printError("Unknown command: " + commandName);
        }
    }

    private String[] parseArguments(String argString) {
        List<String> args = new ArrayList<>();
        // 处理带引号的参数
        return argString.split(" (?=([^\"]*\"[^\"]*\")*[^\"]*$)");
    }

    protected void showHelp() {
        console.printInfo("\nList of available commands：");
        commands.values().stream()
                .distinct()
                .sorted(Comparator.comparing(Command::getName))
                .forEach(cmd -> {
                    console.printInfo(String.format("%-20s - %s",
                            cmd.getName(),
                            cmd.getDescription()));
                });
        console.printInfo("Enter 'help' view this list\n");
    }
}