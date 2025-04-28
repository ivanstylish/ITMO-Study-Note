package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.Product;
import model.User;

public class UpdateHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public UpdateHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }
    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            Long productId = (Long) request.getArgument("id");
            Product newProduct = (Product) request.getArgument("product");

            Product existPro = productDAO.findById(productId);
            if (existPro == null) {
                return CommandResponse.error("Product not found: " + productId);
            }
            if (!existPro.getUserId().equals(user.getId())) {
                return CommandResponse.error("Permission denied: Not product user", null);
            }

            newProduct.setId(productId);
            newProduct.setCreationDate(existPro.getCreationDate());
            newProduct.setUserId(user.getId());

            productDAO.update(newProduct);
            return CommandResponse.success("Product updated: " + productId);
        } catch (Exception | EmptyInputException e) {
            return CommandResponse.error("Update failed: " + e.getMessage());
        } catch (InvalidInputException e) {
            throw new RuntimeException(e);
        }
    }
}
