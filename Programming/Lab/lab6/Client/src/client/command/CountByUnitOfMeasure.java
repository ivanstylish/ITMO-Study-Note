package client.command;

import model.UnitOfMeasure;

public class CountByUnitOfMeasure implements BaseCommand {
    private final UnitOfMeasure unit;
    public CountByUnitOfMeasure(UnitOfMeasure unit) {
        this.unit = unit;
    }

    @Override
    public String getName() {
        return "count_by_unit_of_measure";
    }

    @Override
    public String getDescription() {
        return "вывести количество элементов, значение поля unitOfMeasure которых равно заданному";
    }

    public UnitOfMeasure getUnit() {
        return unit;
    }
}
