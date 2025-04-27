package exception;

public class NetworkException extends Throwable {
    public NetworkException(String s) {
        super(s);
    }

    public NetworkException(String s, Exception e) {
        super(s, e);
    }
}
