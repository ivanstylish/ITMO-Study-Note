package commands.handlers;

import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import user.User;
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
