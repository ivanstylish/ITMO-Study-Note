package command.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.Product;
import model.User;

public class AddIfMinHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public AddIfMinHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {

        try {
            Product newproduct = (Product) request.getArgument("product");
            newproduct.setUserId(user.getId());

            Product minProduct = productDAO.findMinPriceProduct();
            if (minProduct == null || newproduct.getPrice() < minProduct.getPrice()) {
                productDAO.save(newproduct);
                return CommandResponse.success("Product added with ID: " + newproduct.getId());
            }
            return CommandResponse.error("Product price is not the minimum");
        } catch (Exception | InvalidInputException | EmptyInputException e) {
            return CommandResponse.error("AddIfMin failed: " + e.getMessage());
        }
    }

    @Override
    public boolean hasPermission(User user) {
        return super.hasPermission(user) && user.hasPermission("product:write");
    }

}
