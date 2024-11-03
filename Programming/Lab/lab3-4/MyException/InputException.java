package MyException;

import java.io.IOException;

public class InputException extends IOException {
    public String description;

    public InputException(String description){
        this.setDescription(description);
    }
    public void setDescription(String description) {
        this.description = description;
    }
    public String getDescription(){
        return description;
    }
}
