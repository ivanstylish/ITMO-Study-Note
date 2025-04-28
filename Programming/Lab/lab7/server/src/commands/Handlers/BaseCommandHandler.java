package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import model.User;
public abstract class BaseCommandHandler implements CommandHandler {
    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        throw new UnsupportedOperationException("Handler not implemented");
    }

    @Override
    public boolean hasPermission(User user) {
        return user != null && user.isAuthenticated();
    }
}
