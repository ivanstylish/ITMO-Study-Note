package command;

import model.Product;
import util.JsonParser;
import java.util.Arrays;
import java.util.function.BiConsumer;
public class CommandParser {

    private interface CommandHandler extends BiConsumer<String, CommandRequest> {}

    private static final CommandHandler[] COMMAND_HANDLERS = new CommandHandler[CommandType.values().length];

    static {
        // 初始化所有命令处理器
        COMMAND_HANDLERS[CommandType.ADD.ordinal()] = (args, req) -> {
            Product product = parseJsonArgument(args, Product.class);
            req.addArgument("product", product);
        };

        COMMAND_HANDLERS[CommandType.UPDATE.ordinal()] = (args, req) -> {
            String[] parts = validateSplit(args, 2, "update <id> {product_json}");
            req.addArgument("id", parseLong(parts[0]));
            req.addArgument("product", parseJsonArgument(parts[1], Product.class));
        };

        COMMAND_HANDLERS[CommandType.REMOVE_BY_ID.ordinal()] = (args, req) ->
                req.addArgument("id", parseLong(args));

        COMMAND_HANDLERS[CommandType.ADD_IF_MIN.ordinal()] = (args, req) -> {
            Product product = parseJsonArgument(args, Product.class);
            req.addArgument("product", product);
        };

        COMMAND_HANDLERS[CommandType.COUNT_BY_UNIT_OF_MEASURE.ordinal()] = (args, req) ->
                req.addArgument("unit", args.trim());

        COMMAND_HANDLERS[CommandType.MAX_BY_CREATION_DATE.ordinal()] = (args, req) -> {};

        COMMAND_HANDLERS[CommandType.REMOVE_ANY_BY_PRICE.ordinal()] = (args, req) ->
                req.addArgument("price", parseLong(args));

        COMMAND_HANDLERS[CommandType.INSERT_AT.ordinal()] = (args, req) -> {
            String[] parts = validateSplit(args, 2, "insert_at <index> {product_json}");
            req.addArgument("index", Integer.parseInt(parts[0]));
            req.addArgument("product", parseJsonArgument(parts[1], Product.class));
        };
        COMMAND_HANDLERS[CommandType.HELP.ordinal()] = (args, req) -> {};
        COMMAND_HANDLERS[CommandType.CLEAR.ordinal()] = (args, req) -> {};
        COMMAND_HANDLERS[CommandType.INFO.ordinal()] = (args, req) -> {};

    }

    public static CommandRequest parse(String commandLine) {
        String[] parts = commandLine.trim().split(" ", 2);
        if (parts.length == 0 || parts[0].isEmpty()) {
            throw new IllegalArgumentException("Empty command");
        }

        CommandType type = parseCommandType(parts[0]);
        CommandRequest request = new CommandRequest().setCommandType(type);

        if (parts.length > 1) {
            handleArguments(parts[1], type, request);
        }
        return request;
    }

    private static CommandType parseCommandType(String cmd) {
        return Arrays.stream(CommandType.values())
                .filter(t -> t.name().equalsIgnoreCase(cmd))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("unknown command: " + cmd));
    }

    private static void handleArguments(String args, CommandType type, CommandRequest request) {
        CommandHandler handler = COMMAND_HANDLERS[type.ordinal()];
        if (handler == null) {
            throw new IllegalArgumentException("Unimplemented command processor: " + type);
        }
        handler.accept(args, request);
    }

    // ---------------------- 工具方法 ----------------------
    private static <T> T parseJsonArgument(String json, Class<T> type) {
        try {
            if (type == Product.class) {
                return type.cast(JsonParser.parseProduct(json));
            }
            throw new UnsupportedOperationException("Unsupported type: " + type);
        } catch (Exception e) {
            throw new IllegalArgumentException("Parameter parsing failure: " + e.getMessage(), e);
        }
    }

    private static long parseLong(String input) {
        try {
            return Long.parseLong(input.trim());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid numeric format: " + input);
        }
    }

    private static String[] validateSplit(String input, int minParts, String formatHint) {
        String[] parts = input.split(" ", minParts);
        if (parts.length < minParts) {
            throw new IllegalArgumentException("The format of the command is wrong, it should be: " + formatHint);
        }
        return parts;
    }
}
