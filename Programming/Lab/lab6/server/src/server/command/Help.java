package server.command;


import client.command.ExecutableCommand;

public class Help implements ExecutableCommand {
    private final ServerCommandExecutor executor;

    public Help(ServerCommandExecutor executor) {
        this.executor = executor;
    }

    @Override
    public String getDescription() {
        return "вывести справку по доступным командам";
    }

    @Override
    public String getName() {
        return "help";
    }

    @Override
    public String execute() {
        executor.showHelp();
        return null;
    }
}
