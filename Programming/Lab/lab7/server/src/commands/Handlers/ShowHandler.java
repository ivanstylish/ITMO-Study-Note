package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import model.Product;
import model.User;

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
