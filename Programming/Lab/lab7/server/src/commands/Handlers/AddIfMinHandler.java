package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import db.DatabaseConnector;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.Product;
import model.User;

import java.sql.Connection;
import java.sql.SQLException;

public class AddIfMinHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public AddIfMinHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {

        try (Connection conn = DatabaseConnector.getConnection()) {
            conn.setAutoCommit(false);

            Product newProduct = (Product) request.getArgument("product");
            newProduct.setUserId(user.getId());

            Product minProduct = productDAO.findMinPriceProduct(conn);
            if (minProduct == null || newProduct.getPrice() < minProduct.getPrice()) {
                productDAO.save(newProduct, conn);
                conn.commit();
                return CommandResponse.success("Product added with ID: " + newProduct.getId());
            } else {
                conn.rollback();
                return CommandResponse.error("Product price is not the minimum");
            }
        } catch (SQLException | InvalidInputException | EmptyInputException e) {
            return CommandResponse.error("AddIfMin failed: " + e.getMessage());
        }
    }
}