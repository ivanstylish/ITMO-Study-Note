import java.awt.Container;

import java.awt.Color;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.SwingConstants;
import javax.swing.WindowConstants;

public class exp1 extends JFrame {
    /**
     * @param title
     */
    public void CreateFrame(String title) {
        JFrame j = new JFrame(title);
        Container c = j.getContentPane();
        JLabel jl = new JLabel("THIS IS A LABEL");
        jl.setHorizontalAlignment(SwingConstants.CENTER);

        c.add(jl);
        c.setBackground(Color.WHITE);
        j.setVisible(true);
        j.setSize(200, 150);
        j.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
    
}

    public static void main(String[] args) {
        new exp1().CreateFrame("My First Java GUI");
    }
}
