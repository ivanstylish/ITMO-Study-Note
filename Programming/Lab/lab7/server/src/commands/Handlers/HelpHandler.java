package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import command.CommandType;
import logger.Logger;
import model.User;
import java.util.Map;

public class HelpHandler extends BaseCommandHandler {
    private static final Map<CommandType, String> COMMAND_HELP = Map.ofEntries(
            Map.entry(CommandType.HELP, "help - вывести справку по доступным командам"),
            Map.entry(CommandType.INFO, "info - вывести в стандартный поток вывода информацию о коллекции"),
            Map.entry(CommandType.SHOW, "show -  вывести в стандартный поток вывода все элементы коллекции в строковом представлении"),
            Map.entry(CommandType.ADD, "add - добавить новый элемент в коллекцию"),
            Map.entry(CommandType.UPDATE, "update id  - обновить значение элемента коллекции, id которого равен заданному"),
            Map.entry(CommandType.REMOVE_BY_ID, "remove_by_id - удалить элемент из коллекции по его id"),
            Map.entry(CommandType.CLEAR, "clear - очистить коллекцию"),
            Map.entry(CommandType.ADD_IF_MIN, "add_if_min - добавить новый элемент в коллекцию, если его значение меньше, чем у наименьшего элемента этой коллекции"),
            Map.entry(CommandType.COUNT_BY_UNIT_OF_MEASURE,
                    "count_by_unit_of_measure - вывести количество элементов, значение поля unitOfMeasure которых равно заданному"),
            Map.entry(CommandType.MAX_BY_CREATION_DATE,
                    "max_by_creation_date - вывести любой объект из коллекции, значение поля creationDate которого является максимальным"),
            Map.entry(CommandType.EXECUTE_SCRIPT, "execute_script - считать и исполнить скрипт из указанного файла. В скрипте содержатся команды в таком же виде, в котором их вводит пользователь в интерактивном режиме."),
            Map.entry(CommandType.INSERT_AT, "insert_at - добавить новый элемент в заданную позицию"),
            Map.entry(CommandType.REMOVE_ANY_BY_PRICE, "remove_any_by_price - удалить из коллекции один элемент, значение поля price которого эквивалентно заданному"),
            Map.entry(CommandType.SORT, "sort - отсортировать коллекцию в естественном порядке"),
            Map.entry(CommandType.REGISTER, "register - Регистрация нового пользователя"),
            Map.entry(CommandType.AUTH, "auth - Вход пользователя в систему")
    );

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        Logger.info("Processing help command request from client");

        StringBuilder helpText = new StringBuilder("\u001B[34m" + "=== List of available commands ===\n" + "\u001B[0m");
        COMMAND_HELP.values().forEach(desc -> helpText.append("  ").append(desc).append("\n"));
        System.out.println("[SERVER] Help command executed. Help content:\n" + helpText);
        return CommandResponse.success(helpText.toString());
    }
}