package auth;

import model.Product;
import model.User;

public class PermissionChecker {
    /**
     * 验证用户是否拥有操作权限
     */
    public static boolean canModify(User user, Product product) {
        if (product == null) {
            return true;
        }
        return product.getUserId().equals(user.getId());
    }
}
