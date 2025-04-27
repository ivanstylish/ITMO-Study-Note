package command.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import model.Product;
import model.User;


public class AddHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public AddHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }
    @Override
    public CommandResponse handle(CommandRequest request, User user) {

        try {
            Product product = (Product) request.getArgument("product");
            product.setUserId(user.getId());

            productDAO.save(product);
            return CommandResponse.success("Product added with ID: " + product.getId());
        } catch (Exception e) {
            return CommandResponse.error("Add failed: " + e.getMessage());
        }
    }

    @Override
    public boolean hasPermission(User user) {
        return super.hasPermission(user) && user.hasPermission("product:write");
    }
}
