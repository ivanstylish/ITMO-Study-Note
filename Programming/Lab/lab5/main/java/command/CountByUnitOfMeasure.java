package command;

import manager.CollectionManager;
import model.UnitOfMeasure;

public class CountByUnitOfMeasure implements Command {
    private final CollectionManager manager;

    public CountByUnitOfMeasure(CollectionManager manager) {
        this.manager = manager;
    }

    @Override
    public void execute(String[] args) {
        if (args.length < 1) {
            manager.getConsole().printError("Need to provide unit parameter");
            return;
        }
        try {
            UnitOfMeasure unit = UnitOfMeasure.valueOf(args[0].toLowerCase());
            long count = manager.CountByUnitOfMeasure(unit);
            manager.getConsole().printInfo("Number: " + count);
        } catch (IllegalArgumentException e) {
            manager.getConsole().printError("Invalid unit type");
        }
    }

    @Override
    public String getDescription() {
        return "вывести количество элементов, значение поля unitOfMeasure которых равно заданному";
    }

    @Override
    public String getName() {
        return "count_by_unit_of_measure";
    }
}
