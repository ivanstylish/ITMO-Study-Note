package dao;

import db.DatabaseConnector;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.*;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentSkipListSet;

public class ProductDAO {
    private ConcurrentSkipListSet<Product> collection;
    private final Connection connection;

    public ProductDAO() throws SQLException {
        this.connection = DatabaseConnector.getConnection();
    }

    public ConcurrentHashMap<Long, Product> loadAllProducts() throws SQLException {
        ConcurrentHashMap<Long, Product> products = new ConcurrentHashMap<>();
        String query = "SELECT * FROM products p JOIN coordinates c ON p.id = c.product_id " +
                "JOIN organizations o ON p.manufacturer_id = o.id";

        try (Connection con = DatabaseConnector.getConnection();
             Statement st = con.createStatement();
             ResultSet rs = st.executeQuery(query)) {

            while (rs.next()) {
                Product product = mapResultSetToProduct(rs);
                products.put(product.getId(), product);
            }
        } catch (EmptyInputException | InvalidInputException e) {
            throw new RuntimeException(e);
        }
        return products;
    }

    public Product save(Product product, Connection conn) throws SQLException {
        String productSql = "INSERT INTO products (name, price, unit_of_measure, manufacturer_id, user_id, creation_date) "
                + "VALUES (?, ?, ?::unit_of_measure_type, ?, ?, ?) RETURNING id";
        try (PreparedStatement productStmt = conn.prepareStatement(productSql)) {
            productStmt.setString(1, product.getName());
            productStmt.setLong(2, product.getPrice());
            productStmt.setString(3, product.getUnitOfMeasure() != null ? product.getUnitOfMeasure().name() : null);
            productStmt.setInt(4, product.getManufacturerId());
            productStmt.setInt(5, product.getUserId());
            productStmt.setTimestamp(6, new Timestamp(product.getCreationDate().getTime()));

            try (ResultSet rs = productStmt.executeQuery()) {
                if (!rs.next()) {
                    throw new SQLException("Failed to get generated product ID");
                }
                long generatedId = rs.getLong(1);
                product.setId(generatedId); // 确保ID被正确设置
                return product;
            }
        }
    }


    private Product mapResultSetToProduct(ResultSet rs) throws SQLException, EmptyInputException, InvalidInputException {
        Product product = new Product();
        product.setId(rs.getLong("id"));
        product.setName(rs.getString("name"));
        product.setCreationDate(rs.getTimestamp("creation_date"));
        product.setPrice(rs.getLong("price"));

        // 映射Coordinates
        double x = rs.getDouble("x");
        float y = rs.getFloat("y");
        Coordinates coordinates = new Coordinates(x, y);
        product.setCoordinates(coordinates);

        // 映射 UnitOfMeasure
        String unitOfMeasure = rs.getString("unit_of_measure");
        if (unitOfMeasure != null) {
            product.setUnitOfMeasure(UnitOfMeasure.valueOf(unitOfMeasure));
        }

        // 映射Organization
        Organization org = new Organization();
        org.setId(rs.getInt("id"));
        org.setName(rs.getString("name"));
        String org_type = rs.getString("org_type");
        if (org_type != null) {
            org.setType(OrganizationType.valueOf(org_type));
        }
        product.setManufacturer(org);

        product.setUserId(rs.getInt("id"));
        return product;
    }

    public Product findById(Long id) throws SQLException, EmptyInputException, InvalidInputException {
        String sql = "SELECT p.*, c.x, c.y, o.org_name AS org_name, o.org_type AS org_type, p.unit_of_measure AS unit_of_measure " +
                "FROM products p " +
                "LEFT JOIN coordinates c ON p.id = c.product_id " +
                "LEFT JOIN organizations o ON p.manufacturer_id = o.id " +
                "WHERE p.id = ?";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, id);
            try (ResultSet rs = stmt.executeQuery()) {
                return rs.next() ? mapResultSetToProduct(rs) : null;
            }
        }
    }

    public void update(Product product) throws SQLException {
        String sql = "UPDATE products SET name=?, price=?, unit_of_measure=? WHERE id=?";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, product.getName());
            stmt.setLong(2, product.getPrice());
            stmt.setString(3, product.getUnitOfMeasure().name());
            stmt.setLong(4, product.getId());
            stmt.executeUpdate();
        }
    }

    public List<Product> show() throws SQLException {
        List<Product> products = new ArrayList<>();
        String sql = "SELECT p.*, c.x, c.y, o.org_name AS org_name, o.org_type AS org_type, p.unit_of_measure AS unit_of_measure " +
                "FROM products p " +
                "LEFT JOIN coordinates c ON p.id = c.product_id " +
                "LEFT JOIN organizations o ON p.manufacturer_id = o.id";
        try (Connection conn = DatabaseConnector.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                products.add(mapResultSetToProduct(rs));
            }
        } catch (EmptyInputException | InvalidInputException e) {
            throw new RuntimeException(e);
        }
        return products;
    }

    public void clear(int userId, Connection conn) throws SQLException {
        // 删除 coordinates 表的记录
        String deleteCoordinatesSql = "DELETE FROM coordinates WHERE product_id IN (SELECT id FROM products WHERE user_id = ?)";
        try (PreparedStatement stmt = conn.prepareStatement(deleteCoordinatesSql)) {
            stmt.setInt(1, userId);
            stmt.executeUpdate();
        }

        // 删除 products 表的记录
        String deleteProductsSql = "DELETE FROM products WHERE user_id = ?";
        try (PreparedStatement stmt = conn.prepareStatement(deleteProductsSql)) {
            stmt.setInt(1, userId);
            stmt.executeUpdate();
        }

        // 删除 organizations 表中的关联记录（如果存在外键）
        String deleteOrgsSql = "DELETE FROM organizations WHERE id IN (SELECT manufacturer_id FROM products WHERE user_id = ?)";
        try (PreparedStatement stmt = conn.prepareStatement(deleteOrgsSql)) {
            stmt.setInt(1, userId);
            stmt.executeUpdate();
        }
    }

    public void delete(Long id) throws SQLException {
        String sql = "DELETE FROM products WHERE id = ?";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, id);
            stmt.executeUpdate();
        }
    }

    public Product findMinPriceProduct(Connection conn) throws SQLException, InvalidInputException, EmptyInputException {
        String sql = "SELECT p.*, o.org_name AS org_name, o.org_type AS org_type, p.unit_of_measure AS unit_of_measure " +
                "FROM products p " +
                "LEFT JOIN organizations o ON p.manufacturer_id = o.id " +
                "ORDER BY p.price LIMIT 1";
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            return rs.next() ? mapResultSetToProduct(rs) : null;
        }
    }

    public int countByUnitOfMeasure(UnitOfMeasure unit) throws SQLException {
        String sql = "SELECT COUNT(*) FROM products WHERE unit_of_measure = ?";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, unit.name());
            ResultSet rs = stmt.executeQuery();
            return rs.next() ? rs.getInt(1) : 0;
        }
    }

    public Product findLatestProduct() throws SQLException, InvalidInputException, EmptyInputException {
        String sql = "SELECT * FROM products ORDER BY creation_date DESC LIMIT 1";
        try (Connection conn = DatabaseConnector.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            return rs.next() ? mapResultSetToProduct(rs) : null;
        }
    }

    public void insertAt(int index, Product product) {
        List<Product> temp = new ArrayList<>(collection);
        temp.add(index, product);
        collection = new ConcurrentSkipListSet<>(temp);
    }

    public int removeAnyByPrice(long price) throws SQLException {
        try (Connection conn = DatabaseConnector.getConnection()) {
            conn.setAutoCommit(false);

            String deleteCoordinatesSql = "DELETE FROM coordinates WHERE product_id IN (SELECT id FROM products WHERE price = ? LIMIT 1)";
            try (PreparedStatement stmt = conn.prepareStatement(deleteCoordinatesSql)) {
                stmt.setLong(1, price);
                stmt.executeUpdate();
            }

            String deleteProductsSql = "DELETE FROM products WHERE id IN (SELECT id FROM products WHERE price = ? LIMIT 1)";
            try (PreparedStatement stmt = conn.prepareStatement(deleteProductsSql)) {
                stmt.setLong(1, price);
                int rowsAffected = stmt.executeUpdate();
                conn.commit();
                return rowsAffected;
            }
        } catch (SQLException e) {
            throw new SQLException("Remove by price failed: " + e.getMessage(), e);
        }
    }

    public List<Product> showSorted() throws SQLException, InvalidInputException, EmptyInputException {
        String sql = "SELECT p.*, c.x, c.y, o.org_name AS org_name, o.org_type AS org_type " +
                "FROM products p " +
                "LEFT JOIN coordinates c ON p.id = c.product_id " +
                "LEFT JOIN organizations o ON p.manufacturer_id = o.id " +
                "ORDER BY p.price, p.id"; // 按价格和ID排序
        try (Connection conn = DatabaseConnector.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            List<Product> products = new ArrayList<>();
            while (rs.next()) {
                products.add(mapResultSetToProduct(rs));
            }
            return products;
        }
    }

    public Connection getConnection() {
        return connection;
    }
}
