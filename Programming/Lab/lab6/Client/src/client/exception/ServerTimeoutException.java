package client.exception;

public class ServerTimeoutException extends Exception{
    public ServerTimeoutException(String mes){
        super(mes);
    }
}
