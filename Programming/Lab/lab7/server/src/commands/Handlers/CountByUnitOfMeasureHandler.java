package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import model.UnitOfMeasure;
import model.User;

import java.util.List;

public class CountByUnitOfMeasureHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public CountByUnitOfMeasureHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            String unitStr = request.getStringArgument("unit");
            UnitOfMeasure unit = UnitOfMeasure.valueOf(unitStr.toUpperCase());

            int count = productDAO.countByUnitOfMeasure(unit);
            return CommandResponse.success(
                    "Count for " + unit + ": " + count,
                    count
            );
        } catch (IllegalArgumentException e) {
            return CommandResponse.error("Invalid unit. Valid values: "
                    + List.of(UnitOfMeasure.values()));
        } catch (Exception e) {
            return CommandResponse.error("Count failed: " + e.getMessage());
        }
    }
}