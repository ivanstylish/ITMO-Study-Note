package gui;

import exception.EmptyInputException;
import javafx.scene.control.*;
import javafx.scene.layout.GridPane;
import model.Product;


public class ObjectEditorDialog extends Dialog<Void> {
    private final Product product;
    private final TextField nameField = new TextField();

    public ObjectEditorDialog(Product product) {
        this.product = product;
        initUI();
    }

    private void initUI() {
        setTitle("Edit Product");
        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(10);

        nameField.setText(product.getName());
        grid.add(new Label("Product Name:"), 0, 0);
        grid.add(nameField, 1, 0);

        ButtonType saveButtonType = new ButtonType("Save", ButtonBar.ButtonData.OK_DONE);
        getDialogPane().getButtonTypes().addAll(saveButtonType, ButtonType.CANCEL);

        setResultConverter(buttonType -> {
            if (buttonType == saveButtonType) {
                try {
                    product.setName(nameField.getText());
                } catch (EmptyInputException e) {
                    new Alert(Alert.AlertType.ERROR, "Name cannot be empty").show();
                }
            }
            return null;
        });

        getDialogPane().setContent(grid);
    }
}