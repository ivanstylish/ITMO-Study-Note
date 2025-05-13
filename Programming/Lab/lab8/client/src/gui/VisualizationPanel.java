package gui;

import model.Product;

import java.util.ArrayList;
import java.util.List;

import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;

/**
 * 产品实物视觉类(Product Physical Visuals)
 */
public class VisualizationPanel extends Pane {
    private final Canvas canvas = new Canvas();
    private List<Product> products = new ArrayList<>();;

    public VisualizationPanel() {
        this.getChildren().add(canvas);
        canvas.widthProperty().bind(this.widthProperty());
        canvas.heightProperty().bind(this.heightProperty());

        // 鼠标点击事件
        canvas.setOnMouseClicked(e -> products.stream()
                .filter(p -> isPointInProduct(e.getX(), e.getY(), p))
                .findFirst()
                .ifPresent(product -> {
                    // 打开编辑对话框（需实现 JavaFX 版本）
                    ObjectEditorDialog dialog = new ObjectEditorDialog(product);
                    dialog.show();
                }));
    }

    private boolean isPointInProduct(double x, double y, Product product) {
        double scaledX = product.getCoordinates().getX() * canvas.getWidth();
        double scaledY = product.getCoordinates().getY() * canvas.getHeight();
        return x >= scaledX && x <= scaledX + 30 && y >= scaledY && y <= scaledY + 30;
    }

    public void updateProducts(List<Product> products) {
        this.products = (products != null) ? products : new ArrayList<>();;
        redraw();
    }

    private void redraw() {
        GraphicsContext gc = canvas.getGraphicsContext2D();
        gc.clearRect(0, 0, canvas.getWidth(), canvas.getHeight());

        if (products != null) {
            products.forEach(product -> {
                double x = product.getCoordinates().getX() * canvas.getWidth();
                double y = product.getCoordinates().getY() * canvas.getHeight();
                gc.setFill(Color.BROWN); // 可根据用户设置颜色
                gc.fillOval(x, y, 30, 30);
            });
        }
    }
}
