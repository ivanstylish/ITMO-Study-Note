package commands.Handlers;

import auth.AuthService;
import command.CommandRequest;
import command.CommandResponse;
import model.User;
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

        try {
            User newUser = new User(username, password);
            boolean success = authService.register(newUser);
            if (success) {
                return CommandResponse.success("Successful registration!");
            } else {
                return CommandResponse.error("Username already exists", null);
            }
        } catch (SQLException e) {
            return CommandResponse.error("Database error: " + e.getMessage());
        }
    }

    @Override
    public boolean hasPermission(User user) {
        return true;
    }
}