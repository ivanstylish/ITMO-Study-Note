package network;


import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import commandUtil.CommandType;
import exception.NetworkException;
import model.Product;

import javax.swing.*;
import java.util.List;

/**
 * 同步执行通信类(Synchronized execution of communication classes)
 */
public class RealTimeSyncHandler {
    private final ServerProxy proxy;
    private final Runnable updateCB;

    public RealTimeSyncHandler(ServerProxy proxy, Runnable CB) {
        this.proxy = proxy;
        this.updateCB = CB;
        startListening();
    }

    private void startListening() {
        new Thread(() -> {
            while (true) {
                try {
                    CommandResponse response = proxy.sendRequest(
                            new CommandRequest(CommandType.REFRESH)
                    );
                    if (response.isSuccess()) {
                        List<Product> products = (List<Product>) response.getData();
                        SwingUtilities.invokeLater(updateCB);
                    }
                    Thread.sleep(5000);
                } catch (NetworkException | InterruptedException e) {
                    if (e instanceof InterruptedException) {
                        Thread.currentThread().interrupt(); // 恢复中断状态
                    }
                    break; // 退出循环
                }
            }
        }).start();
    }

}
