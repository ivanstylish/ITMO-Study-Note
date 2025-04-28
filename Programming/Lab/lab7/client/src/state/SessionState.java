package state;

import model.User;

import java.time.Instant;

public class SessionState {
    private static User currentUser;
    private static Instant lastActivity;

    public static void refresh() {
        lastActivity = Instant.now();
    }

    public static void login(User user) {
        currentUser = user;
        refresh();
    }

    public static boolean isLoggedIn() {
        return currentUser != null;
    }

    public static User getCurrentUser() {
        return currentUser;
    }
}