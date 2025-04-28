package command;

import auth.AuthProvider;
import dao.UserDAO;
import db.DatabaseConnector;
import exception.NetworkException;
import network.ServerProxy;

import java.net.SocketException;
import java.sql.SQLException;
import java.util.Scanner;

public class RegisterCommand implements Command {
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
            CommandRequest request = new CommandRequest()
                    .setCommandType(CommandType.REGISTER)
                    .addArgument("username", username)
                    .addArgument("password", password);
            CommandResponse response = proxy.sendRequest(request);
            if (response.isSuccess()) {
                System.out.println("Registration successful!");
            } else {
                System.out.println("Registration failed: " + response.getMessage());
            }
        } catch (NetworkException | SocketException | SQLException e) {
            System.err.println("Network error: " + e.getMessage());
        }
    }

    @Override
    public String getDescription() {
        return "Регистрация нового пользователя";
    }

    @Override
    public String getName() {
        return "register";
    }
}