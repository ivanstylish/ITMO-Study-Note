package db;

import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;

public class DatabaseInitializer {
    public static void init() {
        try (Connection conn = DatabaseConnector.getConnection();
             Statement stmt = conn.createStatement()) {

            // 创建 users 表
            stmt.executeUpdate(
                    "CREATE TABLE IF NOT EXISTS users (" +
                            "id SERIAL PRIMARY KEY, " +
                            "username VARCHAR(50) UNIQUE NOT NULL, " +
                            "password_hash VARCHAR(100) NOT NULL)"
            );

            // 创建 products 表及相关联的 coordinates 和 organizations 表
            stmt.executeUpdate(
                    "CREATE TABLE IF NOT EXISTS coordinates (" +
                            "product_id BIGINT PRIMARY KEY, " +
                            "x DOUBLE PRECISION NOT NULL, " +
                            "y REAL NOT NULL)"
            );

            stmt.executeUpdate(
                    "CREATE TABLE IF NOT EXISTS organizations (" +
                            "id SERIAL PRIMARY KEY, " +
                            "org_name VARCHAR(100) NOT NULL)"
            );

            stmt.executeUpdate(
                    "CREATE TABLE IF NOT EXISTS products (" +
                            "id BIGSERIAL PRIMARY KEY, " +
                            "name VARCHAR(100) NOT NULL, " +
                            "creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
                            "price BIGINT NOT NULL, " +
                            "unit_of_measure VARCHAR(50), " +
                            "manufacturer_id INT REFERENCES organizations(id), " +
                            "owner_id INT REFERENCES users(id))"
            );

        } catch (SQLException e) {
            throw new RuntimeException("Failed to initialize database", e);
        }
    }
}