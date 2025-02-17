package command;

import manager.CollectionManager;

public class MaxByCreationDate implements Command {
    private final CollectionManager manager;

    public MaxByCreationDate(CollectionManager manager) {
        this.manager = manager;
    }


    @Override
    public void execute(String[] args) {
        manager.getProductWithMaxDate().ifPresentOrElse(
                product -> manager.getConsole().printInfo(product.toString()),
                () -> manager.getConsole().printInfo("Collection is empty")
        );
    }

    @Override
    public String getDescription() {
        return "вывести любой объект из коллекции, значение поля creationDate которого является максимальным";
    }

    @Override
    public String getName() {
        return "max_by_creation_date";
    }
}
