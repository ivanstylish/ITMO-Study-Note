import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class BounceThread {
    public static void main(String[] args) {
        EventQueue.invokeLater(() -> {
            JFrame frame = new BounceFrame();
            frame.setTitle("BounceThread");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setVisible(true);
        });
    }
}

/**
 * THE FRAME WITH PANEL AND BUTTONS
 */
class BounceFrame extends JFrame{
    private BallComponent comp;
    public static final int STEPS = 1000;
    public static final int DELAY = 5;

    /**
     * Constructs the frame with the component for showing the bouncing ball and
     * Start and Close buttons.
     */

     public BounceFrame() {
        comp = new BallComponent();
        add(comp, BorderLayout.CENTER);
        JPanel buttoPanel = new JPanel();
        addButton(buttoPanel, "Start", event -> addBall());
        addButton(buttoPanel, "Close", event -> System.exit(0));
        add(buttoPanel, BorderLayout.SOUTH);
        pack();
     }
     /**
      * Adds a button to a container.
      * @param c the container
      * @param title the button title
      * @param listener the action listener for the button
      */

      public void addButton(Container c, String title, ActionListener listener) {
        JButton button = new JButton(title);
        button.addActionListener(listener);
        c.add(button);
      }

      /**
       * Adds a bouncing ball to the canvas and starts a thread to make it bounce
       */
      public void addBall() {
        Ball ball = new Ball();
        comp.addBall(ball);
        Runnable r = () -> {
            try {
                for (int i = 0; i < STEPS; i++) {
                    ball.move(comp.getBounds());
                    comp.repaint();
                    Thread.sleep(DELAY);
                }
            }
            catch (InterruptedException e) {
            }
        };
        Thread t = new Thread(r);
        t.start();
      }
}