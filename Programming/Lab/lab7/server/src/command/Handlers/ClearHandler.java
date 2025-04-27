package command.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import model.User;

public class ClearHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public ClearHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            productDAO.clear(user.getId());
            return CommandResponse.success("Collection cleared");
        } catch (Exception e) {
            return CommandResponse.error("Clear failed: " + e.getMessage());
        }
    }
}
