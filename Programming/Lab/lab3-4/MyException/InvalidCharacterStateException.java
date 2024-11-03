package MyException;

public class InvalidCharacterStateException extends Exception{
    public InvalidCharacterStateException(String message) {
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
