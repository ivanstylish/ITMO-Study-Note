package dao;

import model.User;

import java.sql.*;
import java.util.Arrays;

public class UserDAO {
    private final Connection connection;

    public UserDAO(Connection connection) {
        this.connection = connection;
    }

    /**
     * 创建用户(create user)
     */
    public int create(User user) throws SQLException {
        String sql = "INSERT INTO users (username, password_hash, permissions) VALUES (?, ?, ?)";
        try(PreparedStatement stmt = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            stmt.setString(1, user.getUsername());
            stmt.setString(2, user.getPasswordHash());
            stmt.setArray(3, connection.createArrayOf("text", new String[]{"product:write"}));
            stmt.executeUpdate();

            try (ResultSet rs = stmt.getGeneratedKeys()){
                if (rs.next()) {
                    return rs.getInt(1);
                }
            }
            return -1;
        }
    }

    /**
     * 根据用户名查找用户(Find users by username)
     */
    public User findByUsername(String username) throws SQLException {
        String sql = "SELECT * FROM users WHERE username = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)){
            stmt.setString(1, username);
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    User user = new User();
                    user.setId(rs.getInt("id"));
                    user.setUsername(rs.getString("username"));
                    user.setPasswordHash(rs.getString("password_hash"));
                    Array permissionsArray = rs.getArray("permissions");
                    if (permissionsArray != null) {
                        String[] permissions = (String[]) permissionsArray.getArray();
                        user.setPermissions(Arrays.asList(permissions));
                    }
                    return user;
                }
            }
            return null;
        }
    }
}
