package command;

import java.util.Scanner;

public interface Command {
    void execute(String[] parts, Scanner scanner);

    String getDescription();
    String getName();
}