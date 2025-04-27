package command;

public class CommandResponse {
    private final boolean success;
    private final String message;
    private final Object data;

    public CommandResponse(boolean success, String message, Object data) {
        this.message = message;
        this.success = success;
        this.data = data;
    }

    public static CommandResponse success(String s, Object data) {
        return new CommandResponse(true, s, data);
    }

    public boolean isSuccess() {
        return success;
    }

    public String getMessage() {
        return message;
    }

    public static CommandResponse error(String m) {
        return new CommandResponse(false, m, null);
    }

    public static CommandResponse success(String m) {
        return new CommandResponse(true, m, null);
    }
}
