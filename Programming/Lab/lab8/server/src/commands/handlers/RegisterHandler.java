package commands.handlers;

import auth.AuthService;
import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import user.User;
import java.sql.SQLException;

public class RegisterHandler extends BaseCommandHandler {
    private final AuthService authService;

    public RegisterHandler(AuthService authService) {
        this.authService = authService;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User currentUser) {
        String username = request.getStringArgument("username");
        String password = request.getStringArgument("password");

        System.out.println("[DEBUG] Register request - username: " + username + ", password: " + password);

        if (username == null || username.isEmpty() || password == null || password.isEmpty()) {
            System.err.println("[ERROR] Missing parameters: username or password empty");
            return CommandResponse.error("Username or password is missing");
        }

        try {
            boolean success = authService.register(username, password);
            return success ?
                    CommandResponse.success("Registration successful!") :
                    CommandResponse.error("Username already exists");
        } catch (SQLException e) {
            return CommandResponse.error("Database error: " + e.getMessage());
        }
    }

    @Override
    public boolean hasPermission(User user) {
        return true;
    }
}
