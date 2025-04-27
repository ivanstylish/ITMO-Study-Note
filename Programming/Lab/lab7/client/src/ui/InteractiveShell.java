package ui;


import command.Command;
import command.*;
import network.ServerProxy;

import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;


public class InteractiveShell {
    private final Map<String, Command> commands = new HashMap<>();
    private final ServerProxy proxy;
    private final Scanner scanner = new Scanner(System.in);


    public InteractiveShell(ServerProxy proxy) {
        this.proxy = proxy;
        registerCommands();
    }

    private void registerCommands() {
        commands.put("login", new LoginCommand());
    }

    public void start() {
        printWelcome();
        while (true) {
            try {
                System.out.print("> ");
                String input = scanner.nextLine().trim();
                if (input.isEmpty()) {
                    continue;
                }
                String[] parts = input.split(" ");
                Command cmd = commands.get(parts[0].toLowerCase());

                if (cmd != null) {
                    cmd.execute(parts, scanner);
                } else {
                    System.out.println("Unknown command. Enter 'help' to see what's available.");
                }
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public void printWelcome() {
        System.out.println("""
            === Product Management System ===
            Please enter 'help' to see all the available commands
            """);
    }
}
