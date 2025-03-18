package server.command;

import client.command.ExecutableCommand;
import model.UnitOfMeasure;
import server.logging.ServerLogger;
import server.managers.CollectionManager;

public class CountByUnitOfMeasure implements ExecutableCommand {
    private final CollectionManager manager;
    private UnitOfMeasure unit;

    public void setUnit(UnitOfMeasure unit) {
        this.unit = unit;
    }

    public CountByUnitOfMeasure(CollectionManager manager) {
        this.manager = manager;
    }

    @Override
    public String getDescription() {
        return "вывести количество элементов, значение поля unitOfMeasure которых равно заданному";
    }

    @Override
    public String getName() {
        return "count_by_unit_of_measure";
    }

    @Override
    public String execute() {
        try {
            long count = manager.countByUnitOfMeasure(unit);
            ServerLogger.logInfo("Unit " + unit + " number of products: " + count);
        } catch (Exception e) {
            ServerLogger.logError("Failure of statistical units", e);
        }
        return null;
    }
}
