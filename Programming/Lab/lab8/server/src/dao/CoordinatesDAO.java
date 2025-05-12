package dao;

import logger.Logger;
import model.Coordinates;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class CoordinatesDAO {
    public void save(Coordinates coordinates, long productId, Connection conn) throws SQLException {
        String sql = "INSERT INTO coordinates (product_id, x, y) VALUES (?, ?, ?)";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, productId);
            stmt.setDouble(2, coordinates.getX());
            stmt.setFloat(3, coordinates.getY());
            stmt.executeUpdate();
            Logger.info("Insert coordinates: x=" + coordinates.getX() + ", y=" + coordinates.getY());
        }
    }
}