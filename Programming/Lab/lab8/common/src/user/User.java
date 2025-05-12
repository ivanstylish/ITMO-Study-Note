package user;

import java.awt.*;
import java.io.Serial;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 *  用户实体类
 */
public class User implements Serializable{
    @Serial
    private static final long serialVersionUID = 1L;
    private Integer id;
    private String username;
    private String passwordHash;
    private static User currentUser;

    private Color color;

    private List<String> permissions = new ArrayList<>();

    private boolean authenticated = false;

    public User(){}

    public User(Color color) {
        this.color = color;
    }

    public User(String username, String passwordHash) {
        this.username = username;
        this.passwordHash = passwordHash;
    }

    public static User getCurrentUser() {
        return currentUser;
    }

    public Color getColor() {
        return color;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public boolean isAuthenticated() {
        return authenticated;
    }

    public List<String> getPermissions() {
        return permissions;
    }

    public void setPermissions(List<String> permissions) {
        this.permissions = permissions;
    }


    public void setAuthenticated(boolean authenticated) {
        this.authenticated = authenticated;
    }

    public boolean hasPermission(String permission) {
        return permissions.contains(permission) || "admin".equals(this.username);
    }
}