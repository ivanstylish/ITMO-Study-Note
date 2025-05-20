package server.commands;

import common.network.requests.RegisterRequest;
import common.network.requests.Request;
import common.network.responses.RegisterResponse;
import common.network.responses.Response;
import server.managers.AuthManager;

/**
 * The 'register' command. Registers the user.
 */
public class Register extends Command {
  private final AuthManager authManager;
  private final int MAX_USERNAME_LENGTH = 40;

  public Register(AuthManager authManager) {
    super("register", "register a user");
    this.authManager = authManager;
  }

  @Override
  public Response apply(Request request) {
    var req = (RegisterRequest) request;
    var user = req.getUser();
    if (user.getName().length() >= MAX_USERNAME_LENGTH) {
      return new RegisterResponse(user, "The length of the username must be < " + MAX_USERNAME_LENGTH);
    }

    try {
      var newUserId = authManager.registerUser(user.getName(), user.getPassword());

      if (newUserId <= 0) {
        return new RegisterResponse(user, "Failed to create a user.");
      } else {
        return new RegisterResponse(user.copy(newUserId), null);
      }
    } catch (Exception e) {
      return new RegisterResponse(user, e.toString());
    }
  }
}
