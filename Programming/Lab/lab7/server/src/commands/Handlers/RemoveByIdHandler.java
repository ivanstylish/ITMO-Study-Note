package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.Product;
import model.User;


public class RemoveByIdHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public RemoveByIdHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            long id = request.getLongArgument("id");
            Product product = productDAO.findById(id);

            if (product == null) {
                return CommandResponse.error("Product not found", null);
            }
            if (!product.getUserId().equals(user.getId())) {
                return CommandResponse.error("Permission denied", null);
            }

            productDAO.delete(id);
            return CommandResponse.success("Product " + id + " removed");
        } catch (Exception | EmptyInputException | InvalidInputException e) {
            return CommandResponse.error("Remove failed: " + e.getMessage());
        }
    }
}
