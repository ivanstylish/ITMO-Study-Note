package client.parsers;

import client.command.*;
import client.exception.InvalidCommandException;
import client.util.InputHandler;
import exception.EmptyInputException;
import exception.InvalidInputException;
import exception.WrongLengthException;
import model.Product;
import model.UnitOfMeasure;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class ClientCommandParser {
    private final InputHandler inputHandler;
    private final Map<String, CommandFactory> COMMANDS = new HashMap<>();

    public ClientCommandParser(InputHandler inputHandler) {
        this.inputHandler = inputHandler;
        initializeCommands();
    }

    private void initializeCommands() {
        // 基础命令
        COMMANDS.put("help", params -> new Help());
        COMMANDS.put("exit", params -> new Exit());
        COMMANDS.put("clear", params -> new Clear());
        COMMANDS.put("show", params -> new Show());
        COMMANDS.put("info", params -> new Info());
        COMMANDS.put("sort", params -> new Sort());

        // 需要输入 Product 的命令
        COMMANDS.put("add", params -> {
            Product product = inputHandler.inputProduct();
            return new Add(product);
        });
        COMMANDS.put("add_if_min", params -> {
            Product product = inputHandler.inputProduct();
            return new AddIfMin(product);
        });
        COMMANDS.put("insert_at", params -> {
            if (!params.containsKey("index"))
                throw new InvalidCommandException("Missing index parameter");
            int index = Integer.parseInt(params.get("index"));
            Product product = inputHandler.inputProduct();
            return new InsertAt(index, product);
        });

        // 需要 ID 的命令
        COMMANDS.put("update", params -> {
            if (!params.containsKey("id"))
                throw new InvalidCommandException("Missing id parameter");
            long id = parseLong(params.get("id"));
            Product product = inputHandler.inputProduct();
            return new Update(id, product);
        });
        COMMANDS.put("remove_by_id", params -> {
            if (!params.containsKey("id"))
                throw new InvalidCommandException("Missing id parameter");
            long id = parseLong(params.get("id"));
            return new RemoveById(id);
        });

        // 需要特定参数的命令
        COMMANDS.put("count_by_unit_of_measure", params -> {
            UnitOfMeasure unit = inputHandler.inputUnitOfMeasure();
            return new CountByUnitOfMeasure(unit);
        });
        COMMANDS.put("remove_any_by_price", params -> {
            if (!params.containsKey("price"))
                throw new InvalidCommandException("Missing price parameter");
            long price = parseLong(params.get("price"));
            return new RemoveAnyByPrice(price);
        });
        COMMANDS.put("max_by_creation_date", params -> new MaxByCreationDate());
        COMMANDS.put("execute_script", params -> {
            if (!params.containsKey("file"))
                throw new InvalidCommandException("Missing file path");
            return new ExecuteScript(params.get("file"));
        });
    }

    // 参数解析工具方法
    private static final Pattern ARG_PATTERN = Pattern.compile("(\\w+)=([^\\s]+)");

    public BaseCommand parse(String input) throws InvalidCommandException {
        String[] parts = input.trim().split("\\s+", 2);
        if (parts.length == 0) throw new InvalidCommandException("Empty command");

        String cmd = parts[0].toLowerCase();
        Map<String, String> params = parseParams(parts.length > 1 ? parts[1] : "");

        if (!COMMANDS.containsKey(cmd))
            throw new InvalidCommandException("Unknown command: " + cmd);

        try {
            return COMMANDS.get(cmd).create(params);
        } catch (IllegalArgumentException |
                 InvalidInputException | EmptyInputException | WrongLengthException e) {
            throw new InvalidCommandException("Invalid parameters: " + e.getMessage());
        }
    }

    private Map<String, String> parseParams(String args) {
        return Pattern.compile("(\\w+)=([^\\s]+)")
                .matcher(args)
                .results()
                .collect(Collectors.toMap(
                        m -> m.group(1).toLowerCase(),
                        m -> m.group(2),
                        (v1, v2) -> v2
                ));
    }

    private static long parseLong(String value) {
        try {
            return Long.parseLong(value);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid numeric value: " + value);
        }
    }
}