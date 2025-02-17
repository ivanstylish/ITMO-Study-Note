package command;

public class Exit implements Command {

    @Override
    public void execute(String[] args) {
        System.out.println("program exit!");
        System.exit(0);
    }

    @Override
    public String getDescription() {
        return "завершить программу";
    }

    @Override
    public String getName() {
        return "exit";
    }
}
