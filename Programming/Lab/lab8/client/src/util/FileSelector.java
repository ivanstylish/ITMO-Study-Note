package util;

import javafx.stage.Stage;
import javafx.stage.FileChooser;
import java.io.File;

public class FileSelector {
    public File showOpenDialog(Stage ownerStage) {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Open Script File");
        fileChooser.getExtensionFilters().addAll(
                new FileChooser.ExtensionFilter("Text Files", "*.txt"),
                new FileChooser.ExtensionFilter("All Files", "*.*")
        );
        return fileChooser.showOpenDialog(ownerStage);
    }
}
