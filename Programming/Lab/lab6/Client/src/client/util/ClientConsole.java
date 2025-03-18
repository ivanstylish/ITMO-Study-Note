package client.util;

import java.util.NoSuchElementException;
import java.util.Scanner;

public class ClientConsole {
    protected final Scanner scanner = new Scanner(System.in);

    public void printResult(String s) {
        System.out.println("\u001B[34mServer response: " + s + "\u001B[0m");
    }

    public void printError(String s) {
        System.out.println("\u001B[31mERROR: " + s + "\u001B[0m");
    }

    public void printSuccess(String s) {
        System.out.println("\u001b[32m" + s + "\u001B[0m");
    }

    public void printInfo(String s) {
        System.out.println("\u001B[34m" + s + "\u001B[0m");
    }
    public String readLine(String line) {
        System.out.print(line + "-> ");
        System.out.flush();
        try {
            return scanner.nextLine().trim();
        } catch (NoSuchElementException e) {
            return "";
        }
    }
}
