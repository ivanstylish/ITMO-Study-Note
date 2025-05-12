package commands.handlers;

import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import user.User;
public interface CommandHandler {

    CommandResponse handle(CommandRequest request, User user);

    boolean hasPermission(User user);
}
