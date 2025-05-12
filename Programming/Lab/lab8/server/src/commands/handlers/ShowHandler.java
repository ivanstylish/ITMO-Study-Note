package commands.handlers;

import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import dao.ProductDAO;
import model.Product;
import user.User;

import java.sql.SQLException;
import java.util.List;

public class ShowHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public ShowHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            List<Product> products = productDAO.show();
            return CommandResponse.success("All products:" + products);
        } catch (SQLException e) {
            return CommandResponse.error("Show failed: " + e.getMessage());
        }
    }
}
