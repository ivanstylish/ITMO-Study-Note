package command;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class ExecuteScriptCommand implements Command {
    @Override
    public void execute(String[] parts, Scanner scanner) {
        if (parts.length < 2) {
            System.out.println("usage: execute_script <filename>");
            return;
        }

        try (Scanner fileScanner = new Scanner(new File(parts[1]))) {
            while (fileScanner.hasNextLine()) {
                String line = fileScanner.nextLine().trim();
                if (!line.isEmpty()) {
                    // 分发命令处理（需实现命令分发逻辑）
                }
            }
        } catch (FileNotFoundException e) {
            System.err.println("Failed to find the file: " + parts[1]);
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