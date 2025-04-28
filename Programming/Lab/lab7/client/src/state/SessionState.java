package state;

import model.User;

import java.nio.file.Path;
import java.time.Instant;
import java.util.HashSet;
import java.util.Set;

public class SessionState {
    private static User currentUser;
    private static Instant lastActivity;
    private static final Set<Path> runningScripts = new HashSet<>();

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

    public static boolean isScriptRunning(Path scriptPath) {
        return runningScripts.contains(scriptPath);
    }

    // 脚本运行状态
    public static void markScriptRunning(Path scriptPath, boolean isRunning) {
        if (isRunning) {
            runningScripts.add(scriptPath);
        } else {
            runningScripts.remove(scriptPath);
        }
    }

}