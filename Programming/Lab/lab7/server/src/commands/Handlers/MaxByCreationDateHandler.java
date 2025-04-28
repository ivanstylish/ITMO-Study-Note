package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.Product;
import model.User;

public class MaxByCreationDateHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public MaxByCreationDateHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            Product latest = productDAO.findLatestProduct();
            return CommandResponse.success(
                    "Latest product by creation date",
                    latest
            );
        } catch (Exception | InvalidInputException | EmptyInputException e) {
            return CommandResponse.error("Failed to find latest product: " + e.getMessage());
        }
    }
}