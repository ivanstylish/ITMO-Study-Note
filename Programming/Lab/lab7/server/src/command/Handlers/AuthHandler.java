package command.Handlers;


import command.CommandRequest;
import command.CommandResponse;
import dao.UserDAO;
import model.User;
import util.HashUtil;

import java.sql.SQLException;

public class AuthHandler extends BaseCommandHandler {
    private final UserDAO userDAO;

    public AuthHandler(UserDAO userDAO) {
        this.userDAO = userDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User currentUser) {
        String action = request.getStringArgument("action");
        String username = request.getStringArgument("username");
        String password = request.getStringArgument("password");

        try {
            switch (action.toLowerCase()) {
                case "login" -> {
                    return handleLogin(username, password);
                }
                case "register" -> {
                    return handleRegister(username, password);
                }
                default -> {
                    return CommandResponse.error("Unknown authentication operations: " + action);
                }
            }
        } catch (Exception e) {
            return CommandResponse.error("authentication failure: " + e.getMessage());
        }
    }

    // 处理登录逻辑
    private CommandResponse handleLogin(String username, String password) throws SQLException {
        User user = userDAO.findByUsername(username);
        if (user == null) {
            return CommandResponse.error("The user does not exist");
        }

        if (HashUtil.validate(password, user.getPasswordHash())) {
            return CommandResponse.success("Login Successful");
        } else {
            return CommandResponse.error("incorrect password");
        }
    }

    // 处理注册逻辑
    private CommandResponse handleRegister(String username, String password) throws SQLException {
        if (userDAO.exists(username)) {
            return CommandResponse.error("Username already exists");
        }

        String hashedPassword = HashUtil.hash(password);
        User newUser = new User(username, hashedPassword);
        userDAO.save(newUser);

        return CommandResponse.success("Successful registration");
    }

    @Override
    public boolean hasPermission(User user) {
        return true;
    }
}