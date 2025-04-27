import network.ServerProxy;
import java.net.SocketException;

public class ClientMain {
    private ServerProxy proxy;

    public void start() {
        try {
            // 初始化网络代理
            proxy = new ServerProxy("localhost", 12345);

            // 注册关闭钩子
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                proxy.shutDown();
                System.out.println("Client has safely exited");
            }));

            // 启动交互界面
            new ui.InteractiveShell(proxy).start();

        } catch (SocketException e) {
            System.err.println("Network initialization failure: " + e.getMessage());
            System.exit(1);
        }
    }

    public static void main(String[] args) {
        new ClientMain().start();
    }
}