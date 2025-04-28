package commands.Handlers;

import auth.AuthService;
import command.CommandRequest;
import command.CommandResponse;
import model.User;
import state.SessionState;
import util.HashUtil;

import java.sql.SQLException;

public class AuthHandler extends BaseCommandHandler {
    private final AuthService authService;

    public AuthHandler(AuthService authService) {
        this.authService = authService;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User currentUser) {
        String username = request.getStringArgument("username");
        String password = request.getStringArgument("password");

        try {
            User user = authService.authenticate(username, password);
            if (user == null) {
                System.err.println("[AuthHandler] User not found: " + username);
                return CommandResponse.error("User does not exist", null);
            }
            if (HashUtil.validate(password, user.getPasswordHash())) {
                user.setAuthenticated(true);
                SessionState.login(user);
                return CommandResponse.success("Login Successful", user);
            } else {
                return CommandResponse.error("Incorrect password", null);
            }
        } catch (SQLException e) {
            return CommandResponse.error("Database error: ", e.getMessage());
        }
    }

    @Override
    public boolean hasPermission(User user) {
        return true;
    }
}
