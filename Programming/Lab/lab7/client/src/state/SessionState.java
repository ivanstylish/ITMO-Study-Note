package state;

import model.User;

import java.time.Instant;
import java.util.Queue;

public class SessionState {
    private static User currentUser;
    private Instant lastActivity;

    public void refresh() {
        this.lastActivity = Instant.now();
    }

    public static void login(User user) {
        currentUser = user;
    }

    public static boolean isLoggedIn() {
        return currentUser != null;
    }
}
