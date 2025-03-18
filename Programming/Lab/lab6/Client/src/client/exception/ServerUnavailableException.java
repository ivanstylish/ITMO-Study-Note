package client.exception;

import java.rmi.ServerException;

public class ServerUnavailableException extends ServerException {
    public ServerUnavailableException(String s) {
        super(s);
    }
}
