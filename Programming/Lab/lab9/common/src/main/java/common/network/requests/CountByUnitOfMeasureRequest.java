package common.network.requests;

import common.model.UnitOfMeasure;
import common.user.User;
import common.utility.Commands;

public class CountByUnitOfMeasureRequest extends Request{
  private final UnitOfMeasure unit;

  public CountByUnitOfMeasureRequest(UnitOfMeasure unit, User user) {
    super(Commands.COUNT_BY_UNIT_OF_MEASURE, user);
    this.unit = unit;
  }

  public UnitOfMeasure getUnit() {
    return unit;
  }
}
