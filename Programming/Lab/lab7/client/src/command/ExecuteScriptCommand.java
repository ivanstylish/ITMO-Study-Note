package command;

import state.SessionState;
import ui.CommandRegistry;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Scanner;

public class ExecuteScriptCommand implements Command {
    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (!SessionState.isLoggedIn()) {
            System.out.println("Please login first.");
            return;
        }
        if (parts.length < 2) {
            System.out.println("usage: execute_script <filename>");
            return;
        }

        Path scriptPath = Paths.get(parts[1]).toAbsolutePath().normalize();
        if (!Files.exists(scriptPath)) {
            System.err.println("File does not exist or path is invalid:" + scriptPath);
            return;
        }

        if (SessionState.isScriptRunning(scriptPath)) {
            System.err.println("Recursive script execution detected:" + scriptPath);
            return;
        }
        SessionState.markScriptRunning(scriptPath, true); // 标记为正在执行

        try (Scanner fileScanner = new Scanner(scriptPath)) {
            while (fileScanner.hasNextLine()) {
                String line = fileScanner.nextLine().trim();
                if (line.isEmpty()) continue;

                String[] cmdParts = line.split("\\s+");
                String commandName = cmdParts[0].toLowerCase();
                Command command = CommandRegistry.getInstance().getCommand(commandName);
                if (command != null) {
                    command.execute(cmdParts, fileScanner);
                } else {
                    System.out.println("Unknown command:" + cmdParts[0]);
                }
            }
        } catch (FileNotFoundException e) {
            System.err.println("Can't find the file:" + scriptPath);
        } catch (IOException e) {
            throw new RuntimeException(e);
        } finally {
            SessionState.markScriptRunning(scriptPath, false); // 清除标记
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