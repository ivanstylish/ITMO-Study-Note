package command;

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

    public String getStringArgument(String key) {
        Object value = arguments.get(key);
        return (value != null) ? value.toString() : null;
    }

    public Integer getIntegerArgument(String key) {
        Object value = arguments.get(key);
        return (value instanceof Integer) ? (Integer) value : null;
    }

    public Object getData() {
        return data;
    }
}