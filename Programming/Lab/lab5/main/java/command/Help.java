package command;

public class Help implements Command {
    private final CommandExecutor executor;
    public Help(CommandExecutor cmdexe) {
        this.executor = cmdexe;
    }

    @Override
    public void execute(String[] args) {
        executor.showHelp();
    }

    @Override
    public String getDescription() {
        return "вывести справку по доступным командам";
    }

    @Override
    public String getName() {
        return "help";
    }
}
