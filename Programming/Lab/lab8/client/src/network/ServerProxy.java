package network;

import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import commandUtil.CommandType;
import exception.NetworkException;
import logger.Logger;
import model.Product;
import state.ConnectionState;
import util.SerializationUtil;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

/**
 * This class is charging for receiving and sending request from Client
 */
public class ServerProxy {
    private final List<UpdateListener> listeners = new ArrayList<>();
    private static final int TIMEOUT_MS = 3000;
    private static final int MAX_RETRIES = 3;

    private final ConnectionState cs;
    private final InetSocketAddress serverAddress;
    private final DatagramSocket socket;
    private final ExecutorService executor = Executors.newCachedThreadPool();

    public ServerProxy(String host, int port) throws SocketException {
        this.socket = new DatagramSocket();
        this.socket.setSoTimeout(TIMEOUT_MS);
        this.cs = new ConnectionState();
        this.cs.setServerAddress(host, port);
        this.serverAddress = new InetSocketAddress(cs.getServerHost(), cs.getServerPort());
    }

    public void startSyncThread() {
        new Thread(() -> {
            while (true) {
                try {
                    CommandResponse response = sendRequest(new CommandRequest(CommandType.REFRESH));
                    if (response.isSuccess()) {
                        listeners.forEach(l -> l.onCollectionUpdate((List<Product>) response.getData()));
                    }
                    Thread.sleep(1000000);
                } catch (InterruptedException | NetworkException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }).start();
    }

    /**
     * 发送请求并获取响应（同步方法）
     */
    public CommandResponse sendRequest(CommandRequest request) throws NetworkException {
        Logger.info("Sending request: " + request.getType());
        Logger.info("Request arguments: " + request.getArguments());
        try {
            if (!cs.checkConnection()) {
                cs.setConnected(true);
            }
        } catch (Exception e) {
            Logger.error("Failed to connect....: " + e.getMessage());
        }
        for (int i = 0; i < MAX_RETRIES; i++) {
            try {
                byte[] requestData = SerializationUtil.serialize(request);
                Logger.info("Sending request data length: " + requestData.length);

                // 发送请求
                DatagramPacket sendPacket = new DatagramPacket(
                        requestData, requestData.length, serverAddress
                );
                socket.send(sendPacket);

                // 接收响应
                ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
                byte[] buffer = new byte[65507];
                DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
                try {
                    socket.receive(receivePacket);
                    byteStream.write(receivePacket.getData(), 0, receivePacket.getLength());
                    // 循环接收分片
                    while (true) {
                        try {
                            socket.receive(receivePacket);
                            byteStream.write(receivePacket.getData(), 0, receivePacket.getLength());
                        } catch (SocketTimeoutException e) {
                            break;
                        }
                    }
                    byte[] responseData = byteStream.toByteArray();
                    return (CommandResponse) SerializationUtil.deserialize(responseData);
                } catch (IOException | ClassNotFoundException e) {
                    if (i == MAX_RETRIES - 1) {
                        throw new NetworkException("Request failed, last attempt error: " + e.getMessage());
                    }
                    System.out.println("attempts " + (i + 1) + "/" + MAX_RETRIES + " failed. Trying again....");
                    try {
                        Thread.sleep(1000);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                }
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
        return null;
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