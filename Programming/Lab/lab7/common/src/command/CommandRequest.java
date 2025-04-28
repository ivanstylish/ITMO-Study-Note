package command;

import java.io.Serial;
import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class CommandRequest implements Serializable {
    @Serial
    private static final long serialVersionUID = 1L;
    private CommandType commandType;
    private final Map<String, Object> arguments = new HashMap<>();
    private String username;
    private String password;

    // 基础参数操作方法
    public CommandRequest addArgument(String key, Object value) {
        arguments.put(key, value);
        return this;
    }

    public Object getArgument(String key) {
        return arguments.get(key);
    }

    // 类型安全的参数获取方法
    public Long getLongArgument(String key) {
        Object value = arguments.get(key);
        if (value instanceof Long) return (Long) value;
        if (value instanceof Integer) return ((Integer) value).longValue();
        return null;
    }

    public Integer getIntegerArgument(String key) {
        Object value = arguments.get(key);
        if (value instanceof Integer) return (Integer) value;
        return null;
    }

    public String getStringArgument(String key) {
        Object value = arguments.get(key);
        return (value != null) ? value.toString() : null;
    }

    // 特殊命令参数快捷方法
    public Long getId() {
        return getLongArgument("id");
    }


    public Long getPrice() {
        return getLongArgument("price");
    }

    // Getters/Setters
    public CommandType getType() {
        return commandType;
    }

    public CommandRequest setCommandType(CommandType commandType) {

        this.commandType = commandType;
        return this;
    }


    public void setUsername(String username) {
        this.username = username;
    }

    public void setPassword(String password) {
        this.password = password;
    }
    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

}