package ui;

import command.Command;
import network.ServerProxy;


import java.sql.SQLException;
import java.util.NoSuchElementException;
import java.util.Scanner;


public class InteractiveShell implements Console{
    private final CommandRegistry commandRegistry;
    private Scanner scanner = new Scanner(System.in);


    public InteractiveShell(ServerProxy proxy, InputHandler i) throws SQLException {
        this.commandRegistry = new CommandRegistry(proxy, i);
    }

    public String readLine(String line) {
        System.out.print(line + ">");
        System.out.flush();
        try {
            return scanner.nextLine().trim();
        } catch (NoSuchElementException e) {
            return "";
        }
    }

    public void clearInputBuffer() {
        if (scanner.hasNextLine()) {
            scanner.nextLine();
        }
    }
    public void start() {
        printWelcome();
        while (true) {
            try {
                System.out.print("-> ");
                String input = scanner.nextLine().trim();
                if (input.isEmpty()) {
                    continue;
                }
                String[] parts = input.split(" ", 2);
                Command cmd = commandRegistry.getCommand(parts[0]);

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
        printInfo("""
            === Product Management System ===
            Please enter 'help' to see all the available commands
            """);
    }

    public void printInfo(String s) {
        System.out.println("\u001B[34m" + s + "\u001B[0m");
    }

    public void printError(String message) {
        System.out.println("\u001B[31mERROR: " + message + "\u001B[0m");
    }
}
