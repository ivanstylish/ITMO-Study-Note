package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
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

        Connection conn = null;
        try {
            conn = productDAO.getConnection(); // 获取数据库连接
            conn.setAutoCommit(false); // 开启事务

            Product newProduct = (Product) request.getArgument("product");
            newProduct.setUserId(user.getId());

            Product minProduct = productDAO.findMinPriceProduct();
            if (minProduct == null || newProduct.getPrice() < minProduct.getPrice()) {
                // 传递连接参数
                productDAO.save(newProduct, conn);
                conn.commit(); // 提交事务
                return CommandResponse.success("Product added with ID: " + newProduct.getId());
            } else {
                return CommandResponse.error("Product price is not the minimum");
            }
        } catch (InvalidInputException | EmptyInputException | SQLException e) {
            if (conn != null) {
                try {
                    conn.rollback(); // 回滚事务
                } catch (SQLException ex) {
                    ex.printStackTrace();
                }
            }
            return CommandResponse.error("AddIfMin failed: " + e.getMessage());
        } finally {
            if (conn != null) {
                try {
                    conn.setAutoCommit(true);
                    conn.close(); // 关闭连接
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}