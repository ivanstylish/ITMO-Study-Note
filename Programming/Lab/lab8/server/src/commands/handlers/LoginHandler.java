package commands.handlers;

import auth.AuthService;
import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import user.User;
import state.SessionState;
import util.HashUtil;

import java.sql.SQLException;
public class LoginHandler extends BaseCommandHandler {
    private final AuthService authService;

    public LoginHandler(AuthService authService) {
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
