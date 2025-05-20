package common.exceptions;

/**
 * Thrown out if the user already exists when registering.
 */
public class UserAlreadyExistsException extends Exception {
  public UserAlreadyExistsException() {
    super();
  }
}
