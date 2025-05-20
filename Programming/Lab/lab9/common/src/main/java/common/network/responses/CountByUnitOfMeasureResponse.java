package common.network.responses;

import common.utility.Commands;

public class CountByUnitOfMeasureResponse extends Response{
  public final long count;

  public CountByUnitOfMeasureResponse(long count, String error) {
    super(Commands.COUNT_BY_UNIT_OF_MEASURE, error);
    this.count = count;
  }
}
