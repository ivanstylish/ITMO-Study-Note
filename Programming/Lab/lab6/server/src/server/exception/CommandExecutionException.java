package server.exception;

public class CommandExecutionException extends Throwable {
    public CommandExecutionException(String s) {
        super(s);
    }

    public CommandExecutionException(String s, Exception e) {
        super(s, e);
    }
}
