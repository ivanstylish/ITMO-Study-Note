import command.*;
import manager.CollectionManager;
import util.Console;
import util.InputHandler;

public class Main {
    public static void main(String[] args) {
        Console console = new Console();
        CollectionManager manager = new CollectionManager(getDataFilePath(), console);
        InputHandler inputHandler = new InputHandler(manager, console);
        CommandExecutor executor = new CommandExecutor(console);

        executor.registerCommand(new Add(manager, console));
        executor.registerCommand(new AddIfMin(manager, inputHandler));
        executor.registerCommand(new CountByUnitOfMeasure(manager));
        executor.registerCommand(new Clear(manager, inputHandler));
        executor.registerCommand(new Exit());
        executor.registerCommand(new InsertAtIndex(manager, inputHandler));
        executor.registerCommand(new MaxByCreationDate(manager));
        executor.registerCommand(new RemoveAnyByPrice(manager));
        executor.registerCommand(new ExecuteScript(executor, console));
        executor.registerCommand(new Sort(manager));
        executor.registerCommand(new Help(executor));
        executor.registerCommand(new Info(manager));
        executor.registerCommand(new Save(manager));
        executor.registerCommand(new Show(manager));
        executor.registerCommand(new UpdateId(manager, inputHandler));
        executor.registerCommand(new RemoveById(manager));

        console.printInfo( "=== WELCOME TO VARNOTHING'S ===" );
        console.printInfo("=== Product Management System ===");

        while (true) {
            String input = console.readLine("");
            executor.execute(input);
        }
    }
    private static String getDataFilePath() {
        String path = System.getenv("COLLECTION_FILE");
        if (path == null) {
            throw new RuntimeException("Please set the environment variable: COLLECTION_FILE");
        }
        return path;
    }
}
