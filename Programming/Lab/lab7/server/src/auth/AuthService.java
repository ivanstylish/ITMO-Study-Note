package auth;

import dao.UserDAO;
import model.User;

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
        if (userDAO.exists(user.getUsername())) {
            return false;
        }
        user.setPasswordHash(hashPassword(user.getPasswordHash()));
        return userDAO.create(user) > 0;
    }

    /**
     * 用户登录(User login)
     */
    public User authenticate(String username, String password) throws SQLException {
        User user = userDAO.findByUsername(username);
        if (user != null & user.getPasswordHash().equals(hashPassword(password))) {
            return user;
        }
        return null;
    }

    /**
     * SHA-385哈希加密
     */
    private String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-384");
            byte[] hash = md.digest(password.getBytes());
            return Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) {
            throw new RuntimeException("Password hashing failed", e);
        }
    }

}
