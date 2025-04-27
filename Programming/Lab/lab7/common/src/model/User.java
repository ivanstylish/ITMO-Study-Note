package model;

import java.io.Serializable;

/**
 *  用户实体类
 */
public class User implements Serializable{
    private Integer id;
    private String username;
    private String passwordHash;

    private boolean authenticated = false;

    public User() {}

    public User(String username, String passwordHash) {
        this.username = username;
        this.passwordHash = passwordHash;
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

    public void setAuthenticated(boolean authenticated) {
        this.authenticated = authenticated;
    }

    public boolean hasPermission(String permission) {
        return "admin".equals(this.username) && "product:write".equals(permission);
    }
}
