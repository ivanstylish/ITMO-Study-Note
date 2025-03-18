package client.command;

import server.exception.CommandExecutionException;

public interface ExecutableCommand extends BaseCommand {
    String execute() throws CommandExecutionException;
}
