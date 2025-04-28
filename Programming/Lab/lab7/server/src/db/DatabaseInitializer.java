package db;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class DatabaseInitializer {
    public static void init() {
        try (Connection conn = DatabaseConnector.getConnection();
             Statement stmt = conn.createStatement()) {
            // 检查并创建 unit_of_measure_type
            checkAndCreateType(stmt, "unit_of_measure_type",
                    "CREATE TYPE unit_of_measure_type AS ENUM (" +
                            "'CENTIMETERS', 'SQUARE_METERS', 'LITERS', 'MILLILITERS')"
            );

            // 检查并创建 organization_type
            checkAndCreateType(stmt, "organization_type",
                    "CREATE TYPE organization_type AS ENUM (" +
                            "'COMMERCIAL', 'PUBLIC', 'TRUST', 'PRIVATE_LIMITED_COMPANY', 'OPEN_JOINT_STOCK_COMPANY')"
            );

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
                            "org_name VARCHAR(100) NOT NULL, " +
                            "full_name VARCHAR(1125) UNIQUE NOT NULL, " +
                            "type organization_type NOT NULL)"
            );

            stmt.executeUpdate(
                    "CREATE TABLE IF NOT EXISTS products (" +
                            "id BIGSERIAL PRIMARY KEY , " +
                            "name VARCHAR(100) NOT NULL, " +
                            "creation_date TIMESTAMP NOT NULL, " +
                            "price BIGINT NOT NULL, " +
                            "unit_of_measure unit_of_measure_type, " +
                            "manufacturer_id INT REFERENCES organizations(id), " +
                            "owner_id INT REFERENCES users(id))"
            );

        } catch (SQLException e) {
            throw new RuntimeException("Failed to initialize database", e);
        }
    }
    private static void checkAndCreateType(Statement stmt, String typeName, String createSQL) throws SQLException {
        String checkSQL = "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = '" + typeName + "')";
        try (ResultSet rs = stmt.executeQuery(checkSQL)) {
            if (rs.next() && !rs.getBoolean(1)) {
                stmt.executeUpdate(createSQL);
            }
        }
    }
}
