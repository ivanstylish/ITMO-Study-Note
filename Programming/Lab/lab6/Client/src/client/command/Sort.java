package client.command;

public class Sort implements BaseCommand {
    @Override
    public String getName() {
        return "sort";
    }

    @Override
    public String getDescription() {
        return "отсортировать коллекцию в естественном порядке";
    }
}
