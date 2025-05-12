package commands.handlers;

import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import dao.ProductDAO;
import user.User;

public class RemoveByAnyPriceHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public RemoveByAnyPriceHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            long price = request.getLongArgument("price");
            int removed = productDAO.removeAnyByPrice(price);
            return CommandResponse.success(
                    "Removed " + removed + " product(s) with price " + price
            );
        } catch (Exception e) {
            return CommandResponse.error("Remove by price failed: " + e.getMessage());
        }
    }
}
