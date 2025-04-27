package command;

import auth.AuthProvider;
import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.net.SocketException;
import java.util.Scanner;

public class LoginCommand implements Command {

    @Override
    public void execute(String[] parts, Scanner scanner) {
        System.out.print("Username: ");
        String username = scanner.nextLine();
        System.out.print("Password: ");
        String password = scanner.nextLine();

        try {
            ServerProxy proxy = new ServerProxy("localhost", 12345);
            AuthProvider auth = new AuthProvider(proxy);
            if (auth.login(username, password)) {
                SessionState.login(auth.getCurrentUser());
                System.out.println("Login success");
            } else {
                System.out.println("Login failed");
            }
        } catch (NetworkException | SocketException e) {
            System.err.println("Network error: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "User login";
    }

    @Override
    public String getName() {
        return "login";
    }
}
