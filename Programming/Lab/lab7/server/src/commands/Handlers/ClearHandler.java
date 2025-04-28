package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import db.DatabaseConnector;
import model.User;

import java.sql.Connection;

public class ClearHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public ClearHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            Connection conn = DatabaseConnector.getConnection();
            productDAO.clear(user.getId(), conn);
            return CommandResponse.success("Collection cleared");
        } catch (Exception e) {
            return CommandResponse.error("Clear failed: " + e.getMessage());
        }
    }
}