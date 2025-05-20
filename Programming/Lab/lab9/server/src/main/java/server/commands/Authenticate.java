package server.commands;

import common.network.requests.*;
import common.network.responses.*;
import server.managers.AuthManager;

/**
 * Команда 'authenticate'. Аутентифицирует пользователя по логину и паролю.
 */
public class Authenticate extends Command {
  private final AuthManager authManager;

  public Authenticate(AuthManager authManager) {
    super("authenticate", "authenticate the user by login and password");
    this.authManager = authManager;
  }

  @Override
  public Response apply(Request request) {
    var req = (AuthenticateRequest) request;
    var user = req.getUser();
    try {
      var userId = authManager.authenticateUser(user.getName(), user.getPassword());

      if (userId <= 0) {
        return new AuthenticateResponse(user, "There is no such user.");
      } else {
        return new AuthenticateResponse(user.copy(userId), null);
      }
    } catch (Exception e) {
      return new AuthenticateResponse(user, e.toString());
    }
  }
}
