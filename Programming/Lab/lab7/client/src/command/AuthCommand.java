package command;

import auth.AuthProvider;
import dao.UserDAO;
import db.DatabaseConnector;
import exception.NetworkConException;
import exception.NetworkException;
import network.ServerProxy;
import state.SessionState;

import java.net.SocketException;
import java.sql.SQLException;
import java.util.Scanner;
public class AuthCommand implements Command{
    @Override
    public void execute(String[] parts, Scanner scanner) {
        System.out.print("Username: ");
        String username = scanner.nextLine();
        System.out.print("Password: ");
        String password = scanner.nextLine();

        try {
            ServerProxy proxy = new ServerProxy("localhost", 5432);
            UserDAO userDAO = new UserDAO(DatabaseConnector.getConnection());
            AuthProvider auth = new AuthProvider(proxy, userDAO);
            CommandResponse response = auth.login(username, password);
            if (response.isSuccess()) {
                SessionState.login(auth.getCurrentUser());
                System.out.println("Login success");
            } else {
                System.out.println("Login failed: " + response.getMessage());
            }
        } catch (NetworkException | SocketException | NetworkConException | SQLException e) {
            System.err.println("Network error: " + e.getMessage());
        }
        SessionState.refresh();
    }

    @Override
    public String getDescription() {
        return "Вход пользователя в систему";
    }

    @Override
    public String getName() {
        return "auth";
    }
}
