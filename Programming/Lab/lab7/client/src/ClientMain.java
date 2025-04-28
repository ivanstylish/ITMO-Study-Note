import network.ServerProxy;
import ui.CommandRegistry;
import ui.Console;
import ui.InteractiveShell;
import ui.InputHandler;

import java.net.SocketException;
import java.sql.SQLException;

public class ClientMain {
    private ServerProxy proxy;


    public void start() throws SQLException {
        try {
            // 初始化网络代理
            proxy = new ServerProxy("localhost", 5432);
            Console console = new InteractiveShell(proxy, null);
            InputHandler inputHandler1 = new InputHandler(console);
            InteractiveShell shell = new InteractiveShell(proxy, inputHandler1);
            CommandRegistry.initialize(proxy, inputHandler1);
            shell.start();


            // 注册关闭钩子
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                proxy.shutDown();
                System.out.println("Client has safely exited");
            }));

        } catch (SocketException e) {
            System.err.println("Network initialization failure: " + e.getMessage());
            System.exit(1);
        }
    }

    public static void main(String[] args) throws SQLException{
        new ClientMain().start();
    }
}