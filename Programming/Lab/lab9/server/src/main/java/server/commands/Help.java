package server.commands;

import common.network.requests.Request;
import common.network.responses.*;
import server.managers.CommandManager;

/**
 * The 'help' command. Outputs help on available commands
 */
public class Help extends Command {
  private final CommandManager commandManager;

  public Help(CommandManager commandManager) {
    super("help", "display help for available commands");
    this.commandManager = commandManager;
  }

  @Override
  public Response apply(Request request) {
    var helpMessage = new StringBuilder();

    commandManager.getCommands().values().forEach(command -> {
      helpMessage.append(" %-35s%-1s%n".formatted(command.getName(), command.getDescription()));
    });

    return new HelpResponse(helpMessage.toString(), null);
  }
}
