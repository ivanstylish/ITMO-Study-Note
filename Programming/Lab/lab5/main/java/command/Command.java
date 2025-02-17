package command;

public interface Command {
    /**
     * execute commands
     * @param args
     */
    void execute(String[] args);

    /**
     * get description and name of commands
     */
    String getDescription();
    String getName();
}
