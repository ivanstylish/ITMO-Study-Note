package util;

import java.util.NoSuchElementException;
import java.util.Scanner;

public class Console {
    protected final Scanner scanner = new Scanner(System.in);

    public String readLine(String line) {
        System.out.print(line + ">");
        System.out.flush();
        try {
            return scanner.nextLine().trim();
        } catch (NoSuchElementException e) {
            return "";
        }

    }

    public void printSuccess(String message) {
        System.out.println("\u001b[32m" + message + "\u001B[0m");
    }

    public void printError(String message) {
        System.out.println("\u001B[31mERROR: " + message + "\u001B[0m");
    }

    public void printInfo(String message) {
        System.out.println("\u001B[34m" + message + "\u001B[0m");
    }
}
