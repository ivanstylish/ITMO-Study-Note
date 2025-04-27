package command;

import command.Handlers.*;
import dao.ProductDAO;
import dao.UserDAO;
import model.Product;
import model.User;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class CommandProcessor {
    private final Map<CommandType, CommandHandler> handlers = new ConcurrentHashMap<>();

    public void registerHandler(CommandType type, CommandHandler handler) {
        handlers.put(type, handler);
    }

    public CommandProcessor(CommandProcessor cp, ProductDAO productDAO, UserDAO userDAO, ConcurrentHashMap<Long, Product> collection) {
        registerHandler(CommandType.HELP, new HelpHandler());
        registerHandler(CommandType.ADD, new AddHandler(productDAO));
        registerHandler(CommandType.CLEAR, new ClearHandler(productDAO));
        registerHandler(CommandType.INFO, new InfoHandler(collection));
        registerHandler(CommandType.SHOW, new ShowHandler(productDAO));
        registerHandler(CommandType.UPDATE, new UpdateHandler(productDAO));
        registerHandler(CommandType.ADD_IF_MIN, new AddIfMinHandler(productDAO));
        registerHandler(CommandType.AUTH, new AuthHandler(userDAO));
        registerHandler(CommandType.COUNT_BY_UNIT_OF_MEASURE, new CountByUnitOfMeasureHandler(productDAO));
        registerHandler(CommandType.EXECUTE_SCRIPT, new ExecuteScriptHandler(cp));
        registerHandler(CommandType.INSERT_AT, new InsertAtHandler(productDAO));
        registerHandler(CommandType.MAX_BY_CREATION_DATE, new MaxByCreationDateHandler(productDAO));
        registerHandler(CommandType.REMOVE_ANY_BY_PRICE, new RemoveByAnyPriceHandler(productDAO));
        registerHandler(CommandType.REMOVE_BY_ID, new RemoveByIdHandler(productDAO));
        registerHandler(CommandType.SORT, new SortHandler(productDAO));

    }
    public CommandResponse process(CommandRequest request, User user) {
        CommandHandler handler = handlers.get(request.getType());
        if (handler == null) {
            return CommandResponse.error("Unsupported command" + request.getType());
        }

        if (!handler.hasPermission(user)) {
            return CommandResponse.error("Permission denied for command: " + request.getType());
        }

        try {
            return handler.handle(request, user);
        } catch (Exception e) {
            return CommandResponse.error("Command execution failed: " + e.getMessage());
        }
    }
}
