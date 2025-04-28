package ui;

import command.*;
import dao.ProductDAO;
import network.ServerProxy;

import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

public class CommandRegistry {
    private static CommandRegistry instance;
    private final Map<String, Command> commands = new HashMap<>();
    private final ServerProxy proxy;
    private final InputHandler inputHandler;
    ProductDAO productDAO = new ProductDAO();

    public CommandRegistry(ServerProxy proxy, InputHandler inputHandler) throws SQLException {
        this.proxy = proxy;
        this.inputHandler = inputHandler;
        registerCommands();
    }

    private void registerCommands() {
        commands.put("auth", new AuthCommand());
        commands.put("add", new AddCommand(proxy, inputHandler));
        commands.put("help", new HelpCommand(proxy));
        commands.put("update", new UpdateCommand(proxy, inputHandler));
        commands.put("sort", new SortCommand(proxy));
        commands.put("remove_by_id", new RemoveByIdCommand(proxy));
        commands.put("show", new ShowCommand(proxy, productDAO));
        commands.put("max_by_creation_date", new MaxByCreationDateCommand(proxy));
        commands.put("info", new InfoCommand(proxy));
        commands.put("exit", new ExitCommand());
        commands.put("execute_script", new ExecuteScriptCommand());
        commands.put("count_by_unit_of_measure", new CountByUnitOfMeasureCommand(proxy));
        commands.put("clear", new ClearCommand(proxy));
        commands.put("add_if_min", new AddIfMinCommand(proxy));
        commands.put("remove_any_by_price", new RemoveAnyByPriceCommand(proxy));
        commands.put("insert_at", new InsertAtCommand(proxy));
        commands.put("register", new RegisterCommand());
    }

    public static CommandRegistry getInstance() {
        return instance;
    }

    public static void initialize(ServerProxy proxy, InputHandler inputHandler) throws SQLException {
        instance = new CommandRegistry(proxy, inputHandler);
    }

    public Command getCommand(String name) {
        return commands.get(name.toLowerCase());
    }

}