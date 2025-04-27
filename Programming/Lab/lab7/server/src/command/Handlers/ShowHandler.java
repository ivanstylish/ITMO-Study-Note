package command.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import model.User;

public class ShowHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public ShowHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            return CommandResponse.success("Product list" + productDAO.show());
        } catch (Exception e) {
            return CommandResponse.error("Show failed: " + e.getMessage());
        }
    }

    @Override
    public boolean hasPermission(User user) {
        return super.hasPermission(user) &&
                user.hasPermission("product:read");
    }
}
