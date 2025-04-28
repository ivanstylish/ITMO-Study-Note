package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import model.User;
public interface CommandHandler {

    CommandResponse handle(CommandRequest request, User user);

    boolean hasPermission(User user);
}
