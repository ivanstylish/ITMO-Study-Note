package command.Handlers;


import command.CommandResponse;
import model.User;

public interface CommandHandler<T> {

    CommandResponse handle(T request, User user);
    boolean hasPermission(User user);
}
