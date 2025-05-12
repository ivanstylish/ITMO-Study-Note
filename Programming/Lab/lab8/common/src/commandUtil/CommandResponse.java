package commandUtil;

import java.io.Serial;
import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

public class CommandResponse implements Serializable {
    @Serial
    private static final long serialVersionUID = 1L;
    private final boolean success;
    private final String message;
    private final Object data;
    private CommandType type;
    private final Map<String, Object> arguments = new HashMap<>();


    public CommandResponse(boolean success, String message, Object data) {
        this.message = message;
        this.success = success;
        this.data = data;
    }

    public static CommandResponse success(String s, Object data) {
        return new CommandResponse(true, s, data);
    }

    public static CommandResponse error(String s) {
        return new CommandResponse(false, s, null);
    }

    public boolean isSuccess() {
        return success;
    }

    public String getMessage() {
        return message;
    }

    public static CommandResponse error(String m, Object data) {
        return new CommandResponse(false, m, data);
    }

    public static CommandResponse success(String m) {
        return new CommandResponse(true, m, null);
    }

    public Object getData() {
        return data;
    }

    public CommandType getType() {
        return type;
    }
    public void setType(CommandType type) {
        this.type = type;
    }
}