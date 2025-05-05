package network;

import command.CommandRequest;
import command.CommandResponse;
import commands.CommandProcessor;

import model.User;
import state.SessionState;

import java.io.*;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class RequestHandler {
    private final CommandProcessor commandProcessor;
    private static final int THREAD_POOL_SIZE = 10;
    private final ExecutorService executor = Executors.newFixedThreadPool(THREAD_POOL_SIZE);

    public RequestHandler (CommandProcessor commandProcessor) {
        this.commandProcessor = commandProcessor;
    }

    public void handleRequest(ByteBuffer buffer, SocketAddress clientAddr, DatagramChannel channel) {
        executor.submit(() -> {
            try {
                // 反序列化请求
                CommandRequest request = deserializeRequest(buffer);

                // 处理命令（需实现processCommand方法）
                CommandResponse response = processCommand(request);

                // 发送响应
                sendResponse(response, clientAddr, channel);
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }

    private CommandRequest deserializeRequest(ByteBuffer buffer) throws IOException, ClassNotFoundException {
        try (ByteArrayInputStream bis = new ByteArrayInputStream(buffer.array());
             ObjectInputStream ois = new ObjectInputStream(bis)) {
            return (CommandRequest) ois.readObject();
        }
    }

    private void sendResponse(CommandResponse response, SocketAddress clientAddr, DatagramChannel channel)
            throws IOException {
        ByteBuffer buffer = ByteBuffer.wrap(serialize(response));
        channel.send(buffer, clientAddr);
    }

    private byte[] serialize(Object obj) throws IOException {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
             ObjectOutputStream oos = new ObjectOutputStream(bos)) {
            oos.writeObject(obj);
            return bos.toByteArray();
        }
    }

    private CommandResponse processCommand(CommandRequest request) {
        System.out.println("[Server] Processing command: " + request.getType());
        User currentUser = SessionState.getCurrentUser();
        return commandProcessor.process(request, currentUser);
    }
}