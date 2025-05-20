package server.handlers;

import common.network.requests.Request;
import common.network.responses.BadCredentialsResponse;
import common.network.responses.ErrorResponse;
import common.network.responses.Response;
import common.network.responses.NoSuchCommandResponse;
import org.apache.logging.log4j.Logger;
import server.App;
import server.managers.AuthManager;
import server.managers.CommandManager;

import java.sql.SQLException;

public class CommandHandler {
  private final CommandManager manager;
  private final AuthManager authManager;

  private final Logger logger = App.logger;

  public CommandHandler(CommandManager manager, AuthManager authManager) {
    this.manager = manager;
    this.authManager = authManager;
  }

  public Response handle(Request request) {
    if (!request.isAuth()) {
      var user = request.getUser();
      try {
        if (user == null || authManager.authenticateUser(user.getName(), user.getPassword()) <= 0) {
          return new BadCredentialsResponse("Incorrect credentials. Please log in to your account.");
        }
      } catch (SQLException e) {
        logger.error("Unable to execute database query on user authentication.", e);
        return new ErrorResponse("sql_error", "Unable to execute database query on user authentication.");
      }
    }

    var command = manager.getCommands().get(request.getName());
    if (command == null) return new NoSuchCommandResponse(request.getName());
    return command.apply(request);
  }
}
