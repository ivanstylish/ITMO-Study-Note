package dao;

import db.DatabaseConnector;
import exception.EmptyInputException;
import exception.InvalidInputException;
import model.Coordinates;
import model.Organization;
import model.Product;
import model.UnitOfMeasure;

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

        try(Connection con = DatabaseConnector.getConnection();
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

    public Product save(Product product) throws SQLException {
        String sql = "INSERT INTO products (name, coordinates, price, unit_of_measure, manufacturer_id, owner_id) "
                + "VALUES (?, ?, ?, ?, ?, ?) RETURNING id";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, product.getName());
            stmt.setObject(2, product.getCoordinates());
            stmt.setLong(3, product.getPrice());
            stmt.setString(4, product.getUnitOfMeasure().name());
            stmt.setInt(5, product.getManufacturer().getId());
            stmt.setInt(6, product.getUserId());

            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                product.setId(rs.getLong(1));
            }
            return product;
        }
    }

    private Product mapResultSetToProduct(ResultSet rs) throws SQLException, EmptyInputException, InvalidInputException {
        Product product = new Product();
        product.setId(rs.getLong("id"));
        product.setName(rs.getString("name"));
        product.setCreationDate(rs.getTimestamp("creation_date"));
        product.setPrice(rs.getLong("price"));

        // 映射Coordinates
        Coordinates coordinates = new Coordinates();
        coordinates.setX(rs.getDouble("x"));
        coordinates.setY(rs.getFloat("y"));
        product.setCoordinates(coordinates);

        // 映射Organization
        Organization org = new Organization();
        org.setId(rs.getInt("organization_id"));
        org.setName(rs.getString("org_name"));
        product.setManufacturer(org);

        product.setUserId(rs.getInt("owner_id"));
        return product;
    }

    public Product findById(Long id) throws SQLException, EmptyInputException, InvalidInputException {
        String sql = "SELECT * FROM products WHERE id = ?";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, id);
            ResultSet rs = stmt.executeQuery();
            return rs.next() ? mapResultSetToProduct(rs) : null;
        }
    }

    public void update(Product product) throws SQLException {
        String sql = "UPDATE products SET name=?, coordinates=?, price=?, unit_of_measure=? WHERE id=?";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, product.getName());
            stmt.setObject(2, product.getCoordinates());
            stmt.setLong(3, product.getPrice());
            stmt.setString(4, product.getUnitOfMeasure().name());
            stmt.setLong(5, product.getId());
            stmt.executeUpdate();
        }
    }

    public List<Product> show() throws SQLException {
        List<Product> products = new ArrayList<>();
        String sql = "SELECT * FROM products";
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

    public void clear(int ownerId) throws SQLException {
        String sql = "DELETE FROM products WHERE owner_id = ?";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, ownerId);
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

    public Product findMinPriceProduct() throws SQLException, InvalidInputException, EmptyInputException {
        String sql = "SELECT * FROM products ORDER BY price ASC LIMIT 1";
        try (Connection conn = DatabaseConnector.getConnection();
             Statement stmt = conn.createStatement();
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
        String sql = "DELETE FROM products WHERE price = ? LIMIT 1";
        try (Connection conn = DatabaseConnector.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, price);
            return stmt.executeUpdate();
        }
    }

    public void sortCollection() {
        ConcurrentSkipListSet<Product> sortedSet = new ConcurrentSkipListSet<>((p1, p2) -> {
            int priceCompare = Long.compare(p1.getPrice(), p2.getPrice());
            return priceCompare != 0 ? priceCompare : Long.compare(p1.getId(), p2.getId());
        });
        sortedSet.addAll(collection);
        collection = sortedSet;
    }
}
