package gui;

import javafx.scene.control.ComboBox;
import util.LocalizationManager;

import java.util.Locale;
import java.util.Map;

public class LanguageSwitcher extends ComboBox<String> {
    private static final Map<String, Locale> LANGUAGE_MAP = Map.of(
            "English (UK)", Locale.UK,
            "Русский", new Locale("ru"),
            "Македонски", new Locale("mk"),
            "Dansk", new Locale("da")
    );

    public LanguageSwitcher() {
        super();
        this.getItems().addAll(LANGUAGE_MAP.keySet());
        this.getSelectionModel().selectedItemProperty().addListener((obs, oldVal, newVal) -> {
            Locale locale = LANGUAGE_MAP.get(newVal);
            LocalizationManager.setLocale(locale);
        });
    }
}