package exception;

public class EmptyInputException extends InvalidInputException{
    public EmptyInputException(String fieldName){
        super(fieldName + " cannot be empty or null!");
    }
}
