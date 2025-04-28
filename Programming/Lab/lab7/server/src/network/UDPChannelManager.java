package network;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.util.Iterator;

public class UDPChannelManager {
    private final DatagramChannel channel;
    private final Selector selector;
    private final RequestHandler requestHandler;

    public UDPChannelManager(int port, RequestHandler handler) throws IOException {
        this.channel = (DatagramChannel) DatagramChannel.open()
                .bind(new InetSocketAddress(port))
                .configureBlocking(false);
        this.selector = Selector.open();
        this.requestHandler = handler;
        channel.register(selector, SelectionKey.OP_READ);
    }

    public void start() throws IOException {
        while (true) {
            selector.select();
            Iterator<SelectionKey> keys = selector.selectedKeys().iterator();

            while (keys.hasNext()) {
                SelectionKey key = keys.next();
                keys.remove();

                if (key.isReadable()) {
                    handleReadable(key);
                }
            }
        }
    }

    private void handleReadable(SelectionKey key) {
        DatagramChannel channel = (DatagramChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(65507);

        try {
            SocketAddress clientAddr = channel.receive(buffer);
            if (clientAddr != null) {
                System.out.println("Received request from " + clientAddr);
                buffer.flip(); // 切换为读模式
                requestHandler.handleRequest(buffer, clientAddr, channel);
            }
        } catch (IOException e) {
            System.err.println("Error handling request: " + e.getMessage());
        }
    }
}

