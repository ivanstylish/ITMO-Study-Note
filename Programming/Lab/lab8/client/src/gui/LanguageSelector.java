package gui;

import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Dialog;
import javafx.scene.layout.VBox;
import util.LocalizationManager;
import java.util.Locale;
import java.util.Map;

public class LanguageSelector extends Dialog<Void> {
    private static final Map<String, Locale> LANGUAGE_MAP = Map.of(
            "English (UK)", Locale.UK,
            "Русский", new Locale("ru"),
            "Македонски", new Locale("mk"),
            "Dansk", new Locale("da")
    );

    public LanguageSelector() {
        setTitle("Select Language");
        ComboBox<String> comboBox = new ComboBox<>();
        comboBox.getItems().addAll(LANGUAGE_MAP.keySet());

        Button confirmButton = new Button("Confirm");
        confirmButton.setOnAction(e -> {
            String selected = comboBox.getValue();
            Locale locale = LANGUAGE_MAP.get(selected);
            LocalizationManager.setLocale(locale);
            close();
        });

        VBox vbox = new VBox(10);
        vbox.getChildren().addAll(comboBox, confirmButton);
        getDialogPane().setContent(vbox);
    }
}
