package network;

import command.CommandRequest;
import command.CommandResponse;
import exception.NetworkException;
import util.SerializationUtil;

import java.io.IOException;
import java.net.*;
import java.util.Arrays;
import java.util.concurrent.*;

/**
 * This class is charging for receiving and sending request from Client
 */
public class ServerProxy {
    private static final int TIMEOUT_MS = 3000;
    private static final int MAX_RETRIES = 3;

    private final InetSocketAddress serverAddress;
    private final DatagramSocket socket;
    private final ExecutorService executor = Executors.newCachedThreadPool();

    public ServerProxy(String host, int port) throws SocketException {
        this.serverAddress = new InetSocketAddress(host, port);
        this.socket = new DatagramSocket();
        this.socket.setSoTimeout(TIMEOUT_MS);
    }

    /**
     * 发送请求并获取响应（同步方法）
     */
    public CommandResponse sendRequest(CommandRequest request) throws NetworkException {
        for (int i = 0; i < MAX_RETRIES; i++) {
            try {
                byte[] requestData = SerializationUtil.serialize(request);

                // 发送请求
                DatagramPacket sendPacket = new DatagramPacket(
                        requestData, requestData.length, serverAddress
                );
                socket.send(sendPacket);

                // 接收响应
                byte[] buffer = new byte[65507];
                DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
                socket.receive(receivePacket);

                return (CommandResponse) SerializationUtil.deserialize(buffer);
            } catch (IOException | ClassNotFoundException e) {
                if (i == MAX_RETRIES - 1) {
                    throw new NetworkException("Request failed, last attempt error: " + e.getMessage());
                }
                System.out.println("attempts " + (i+1) + "/" + MAX_RETRIES + " failed. Trying again....");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }
        }
        throw new NetworkException("Unexpected error");
    }

    public CommandResponse receiveResponse() throws IOException, ClassNotFoundException {
        byte[] buffer = new byte[65507];
        DatagramPacket packet = new DatagramPacket(buffer, buffer.length);

        for (int i = 0; i < MAX_RETRIES; i++) {
            try {
                socket.receive(packet);
                return (CommandResponse) SerializationUtil.deserialize(
                        Arrays.copyOf(packet.getData(), packet.getLength())
                );
            } catch (SocketTimeoutException e) {
                if (i == MAX_RETRIES - 1) throw e;
            }
        }
        throw new IOException("No response after " + MAX_RETRIES + " attempts");
    }

    /**
     * 异步发送请求
     */
    public CompletableFuture<CommandResponse> sendAsync(CommandRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return sendRequest(request);
            }catch (NetworkException e) {
                throw new CompletionException(e);
            }
        }, executor);
    }

    /**
     * 关闭网络连接
     */
    public void shutDown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(800, TimeUnit.MILLISECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
        socket.close();
    }
}
