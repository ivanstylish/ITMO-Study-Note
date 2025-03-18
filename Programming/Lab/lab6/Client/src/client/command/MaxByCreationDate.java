package client.command;

public class MaxByCreationDate implements BaseCommand {
    @Override
    public String getName() {
        return "max_by_creation_date";
    }

    @Override
    public String getDescription() {
        return "вывести любой объект из коллекции, значение поля creationDate которого является максимальным";
    }
}
