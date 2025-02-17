package command;

import util.Console;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class ExecuteScript implements Command {
    private final CommandExecutor executor;
    private final Console console;

    public ExecuteScript(CommandExecutor executor, Console console) {
        this.executor = executor;
        this.console = console;
    }

    @Override
    public void execute(String[] args) {
        if (args.length < 1) {
            console.printError("Script file path is required");
        }
        try (Scanner scanner = new Scanner(new File(args[0]))){
            while (scanner.hasNextLine()) {
                String command = scanner.nextLine().trim();
                if (!command.isEmpty()) {
                    console.printInfo("execute command: " + command);
                    executor.execute(command);
                }
            }
        }catch (FileNotFoundException e) {
            console.printError("File not found: " + args[0]);
        }
    }

    @Override
    public String getDescription() {
        return "считать и исполнить скрипт из указанного файла. В скрипте содержатся команды в таком же виде, в котором их вводит пользователь в интерактивном режиме.";
    }

    @Override
    public String getName() {
        return "execute_script";
    }
}
