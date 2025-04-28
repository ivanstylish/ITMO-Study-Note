package commands.Handlers;

import command.CommandRequest;
import command.CommandResponse;
import dao.ProductDAO;
import model.Product;
import model.User;

public class InsertAtHandler extends BaseCommandHandler {
    private final ProductDAO productDAO;

    public InsertAtHandler(ProductDAO productDAO) {
        this.productDAO = productDAO;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            int index = request.getIntegerArgument("index");
            Product product = (Product) request.getArgument("product");
            product.setUserId(user.getId());

            // 实现插入逻辑（需要数据库支持或内存操作）
            productDAO.insertAt(index, product);
            return CommandResponse.success("Inserted at index " + index);
        } catch (Exception e) {
            return CommandResponse.error("Insert failed: " + e.getMessage());
        }
    }
}