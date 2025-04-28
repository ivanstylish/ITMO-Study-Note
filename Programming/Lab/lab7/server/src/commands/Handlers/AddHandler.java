package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.CoordinatesDAO;
import dao.OrganizationDAO;
import dao.ProductDAO;
import db.DatabaseConnector;
import logger.Logger;
import model.Organization;
import model.Product;
import model.User;

import java.sql.Connection;
import java.sql.SQLException;


public class AddHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;
    private final OrganizationDAO organizationDAO;
    private final CoordinatesDAO coordinatesDAO;

    public AddHandler(ProductDAO productDAO, OrganizationDAO organizationDAO, CoordinatesDAO coordinatesDAO) {
        this.productDAO = productDAO;
        this.organizationDAO = organizationDAO;
        this.coordinatesDAO = coordinatesDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {

        Connection conn = null;
        try {
            conn = DatabaseConnector.getConnection(); // 获取同一连接
            conn.setAutoCommit(false); // 开启事务

            Product product = (Product) request.getArgument("product");
            product.setUserId(user.getId());

            // 保存制造商到organizations表（传递连接）
            Organization manufacturer = product.getManufacturer();
            int manufacturerId = organizationDAO.save(manufacturer, conn);
            product.setManufacturerId(manufacturerId);

            // 保存产品到products表（传递连接）
            Product savedProduct = productDAO.save(product, conn);
            long productId = savedProduct.getId();

            // 保存坐标到coordinates表（传递连接）
            coordinatesDAO.save(product.getCoordinates(), productId, conn);

            conn.commit();
            return CommandResponse.success("Product added successfully, ID: " + productId);
        } catch (Exception e) {
            if (conn != null) {
                try {
                    conn.rollback();
                } catch (SQLException ex) {
                    Logger.error("Transaction rollback failed: " + ex.getMessage());
                }
            }
            Logger.error("Failed to add: " + e.getMessage());
            return CommandResponse.error("Add Error: " + e.getMessage());
        } finally {
            if (conn != null) {
                try {
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException e) {
                    Logger.error("Connection closure error: " + e.getMessage());
                }
            }
        }
    }
}
