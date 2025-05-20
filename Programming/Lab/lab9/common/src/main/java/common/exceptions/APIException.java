package common.exceptions;

/**
 * Thrown if there is an error in the server response
 */
public class APIException extends Exception {
  public APIException(String message) {
    super(message);
  }
}
