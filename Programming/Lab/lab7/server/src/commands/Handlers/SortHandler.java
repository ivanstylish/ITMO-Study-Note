package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.Product;
import model.User;

import java.sql.SQLException;
import java.util.List;

public class SortHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public SortHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            List<Product> sortedProducts = productDAO.showSorted();
            return CommandResponse.success("Collection sorted by price and ID:" + sortedProducts);
        } catch (SQLException | InvalidInputException | EmptyInputException e) {
            return CommandResponse.error("Sort failed: " + e.getMessage());
        }
    }
}