package dao;

import db.DatabaseConnector;
import model.Organization;
import java.sql.*;
public class OrganizationDAO {
    public int save(Organization org, Connection conn) throws SQLException {
        String sql = "INSERT INTO organizations (org_name, full_name, org_type) VALUES (?, ?, ?::organization_type) RETURNING id";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, org.getName());
            stmt.setString(2, org.getFullName());
            stmt.setString(3, org.getType().name());

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt("id");
                }
                throw new SQLException("Unable to save organization information");
            }
        }
    }
}