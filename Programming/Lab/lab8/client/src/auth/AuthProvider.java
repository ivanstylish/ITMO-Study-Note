package auth;

import user.User;


public class AuthProvider {
    public static User currentUser = null;
    public static String currentLanguage = "English";

    public static User getCurrentUser() {
        return currentUser;
    }

    public static void setCurrentUser(User user) {
        currentUser = user;
    }

    public static String getCurrentLanguage() {
        return currentLanguage;
    }

    public static void setCurrentLanguage(String language) {
        currentLanguage = language;
    }
}
