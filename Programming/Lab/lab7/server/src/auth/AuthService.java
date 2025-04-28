package auth;

import dao.UserDAO;
import model.User;
import util.HashUtil;

import java.security.MessageDigest;
import java.sql.SQLException;
import java.util.Base64;

public class AuthService {
    private final UserDAO userDAO;

    public AuthService(UserDAO userDAO) {
        this.userDAO = userDAO;
    }

    /**
     * 用户注册 (User Registration)
     */

    public boolean register(User user) throws SQLException {
        String rawPassword = user.getPasswordHash(); // 假设传入的是明文密码
        String hashedPassword = hashPassword(rawPassword);
        user.setPasswordHash(hashedPassword);
        System.out.println("[DEBUG] Registered Hash: " + hashedPassword);
        return userDAO.create(user) > 0;
    }

    /**
     * 用户登录(User login)
     */
    public User authenticate(String username, String password) throws SQLException {
        User user = userDAO.findByUsername(username);
        if (user != null && HashUtil.validate(password, user.getPasswordHash())) {
            System.out.println("[DEBUG] Validating password for: " + username + ", stored hash: " + user.getPasswordHash());
            return user;
        }
        return null;
    }

        /**
         * SHA-384哈希加密
         */
    public String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-384");
            byte[] hash = md.digest(password.getBytes());
            return Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) {
            throw new RuntimeException("Password hashing failed", e);
        }
    }

}
