package commands;

import auth.AuthService;
import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import commandUtil.CommandType;
import commands.handlers.*;
import dao.CoordinatesDAO;
import dao.OrganizationDAO;
import dao.ProductDAO;
import model.Product;
import user.User;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class CommandProcessor {
    private final Map<CommandType, CommandHandler> handlers = new ConcurrentHashMap<>();

    public void registerHandler(CommandType type, CommandHandler handler) {
        handlers.put(type, handler);
    }

    public CommandProcessor(CommandProcessor cp, AuthService authService, OrganizationDAO od, CoordinatesDAO cd, ProductDAO productDAO, ConcurrentHashMap<Long, Product> collection) {
        registerHandler(CommandType.HELP, new HelpHandler());
        registerHandler(CommandType.ADD, new AddHandler(productDAO, od, cd));
        registerHandler(CommandType.CLEAR, new ClearHandler(productDAO));
        registerHandler(CommandType.INFO, new InfoHandler(collection));
        registerHandler(CommandType.SHOW, new ShowHandler(productDAO));
        registerHandler(CommandType.UPDATE, new UpdateHandler(productDAO));
        registerHandler(CommandType.ADD_IF_MIN, new AddIfMinHandler(productDAO));
        registerHandler(CommandType.LOGIN, new LoginHandler(authService));
        registerHandler(CommandType.COUNT_BY_UNIT_OF_MEASURE, new CountByUnitOfMeasureHandler(productDAO));
        registerHandler(CommandType.EXECUTE_SCRIPT, new ExecuteScriptHandler(cp));
        registerHandler(CommandType.INSERT_AT, new InsertAtHandler(productDAO));
        registerHandler(CommandType.MAX_BY_CREATION_DATE, new MaxByCreationDateHandler(productDAO));
        registerHandler(CommandType.REMOVE_ANY_BY_PRICE, new RemoveByAnyPriceHandler(productDAO));
        registerHandler(CommandType.REMOVE_BY_ID, new RemoveByIdHandler(productDAO));
        registerHandler(CommandType.SORT, new SortHandler(productDAO));
        registerHandler(CommandType.REGISTER, new RegisterHandler(authService));

    }
    public CommandResponse process(CommandRequest request, User user) {
        CommandHandler handler = handlers.get(request.getType());
        if (handler == null) {
            return CommandResponse.error("Unsupported command " , request.getType());
        }

        if (!handler.hasPermission(user)) {
            return CommandResponse.error("Permission denied for command " , request.getType());
        }

        try {
            return handler.handle(request, user);
        } catch (Exception e) {
            return CommandResponse.error("Command execution failed " , e.getMessage());
        }
    }
}