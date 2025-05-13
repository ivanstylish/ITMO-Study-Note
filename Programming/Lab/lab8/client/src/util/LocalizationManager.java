package util;

import java.util.Locale;
import java.util.MissingResourceException;
import java.util.ResourceBundle;

public class LocalizationManager {
    private ResourceBundle bundle;
    private static Locale currentLocale = Locale.UK;
    private static volatile LocalizationManager instance;

    // 私有构造函数，禁止外部实例化
    private LocalizationManager() {
        loadBundle();
    }

    // 单例获取方法（双重检查锁定）
    public static LocalizationManager getInstance() {
        if (instance == null) {
            synchronized (LocalizationManager.class) {
                if (instance == null) {
                    instance = new LocalizationManager();
                }
            }
        }
        return instance;
    }

    // 加载资源包
    private void loadBundle() {
        try {
            bundle = ResourceBundle.getBundle("Messages", currentLocale);
            System.out.println("[DEBUG] Loaded bundle: " + bundle.getLocale());
        } catch (MissingResourceException e) {
            System.err.println("Failed to load bundle for locale: " + currentLocale);
            bundle = ResourceBundle.getBundle("Messages", Locale.UK); // 回到默认语言
        }
    }

    // 设置语言并重新加载资源包
    public static void setLocale(Locale locale) {
        currentLocale = locale;
        System.out.println("[DEBUG] Setting locale: " + locale);
        getInstance().loadBundle(); // 通过实例方法加载
        System.out.println("[DEBUG] Loaded bundle: " + getInstance().bundle);
        fireLanguageChanged();
    }

    // 获取本地化字符串
    public static String getString(String key) {
        return getInstance().bundle.getString(key);
    }

    public static void fireLanguageChanged() {
        Event.publish();
    }
    public void setBundle(ResourceBundle bundle) {
        this.bundle = bundle;
    }
}