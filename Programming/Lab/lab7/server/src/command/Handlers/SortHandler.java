package command.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import model.User;

public class SortHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public SortHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            productDAO.sortCollection();
            return CommandResponse.success("Collection sorted successfully");
        } catch (Exception e) {
            return CommandResponse.error("Sort failed: " + e.getMessage());
        }
    }
}