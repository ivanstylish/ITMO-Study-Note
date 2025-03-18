package server.network;

import client.command.BaseCommand;
import server.command.ServerCommandExecutor;
import server.exception.CommandExecutionException;
import server.logging.ServerLogger;
import util.SerializationUtils;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;


public class ServerUdpListener {
    protected final ServerCommandExecutor executor;
    private final int port;

    public ServerUdpListener(ServerCommandExecutor executor, int port) throws IOException {
        this.executor = executor;
        this.port = port;
    }

    public void start() throws IOException {
        try (DatagramChannel channel = DatagramChannel.open()) {
            channel.bind(new InetSocketAddress(port));
            ByteBuffer buffer = ByteBuffer.allocate(4096);

            ServerLogger.logServerStart(port);

            while (true) {
                buffer.clear();
                // 接收数据并获取客户端地址
                SocketAddress clientSocketAddress = channel.receive(buffer);
                buffer.flip();

                // 记录客户端请求
                if (clientSocketAddress != null) {
                    InetSocketAddress inetAddr = (InetSocketAddress) clientSocketAddress;
                    String clientInfo = inetAddr.getAddress().getHostAddress() + ":" + inetAddr.getPort();
                    ServerLogger.logNewRequest(clientInfo);
                }

                // 处理请求
                byte[] data = new byte[buffer.remaining()];
                buffer.get(data);
                handleRequest(data, channel, clientSocketAddress);
                buffer.clear();
            }
        }
    }

    private void handleRequest(byte[] data, DatagramChannel channel, SocketAddress clientAddress) throws IOException {
        try {
            BaseCommand command = (BaseCommand) SerializationUtils.deserialize(data);
            ServerLogger.logInfo("[Server] Received command: " + command.getClass().getSimpleName());

            Object response = executor.execute(command);
            byte[] responseData = SerializationUtils.serialize(response);
            ByteBuffer buffer = ByteBuffer.wrap(responseData);
            channel.send(buffer, clientAddress);

        } catch (Exception | CommandExecutionException e) {
            ServerLogger.logError("Failure to process request", e);
            byte[] errorData = SerializationUtils.serialize("Error: " + e.getMessage());
            ByteBuffer errorBuffer = ByteBuffer.wrap(errorData);
            try {
                channel.send(errorBuffer, clientAddress);
            } catch (IOException ex) {
                ServerLogger.logError("Failed to send error response", ex);
            }
        }
    }
}