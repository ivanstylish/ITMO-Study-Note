package client.network;

import client.command.Add;
import client.command.BaseCommand;
import client.exception.ServerTimeoutException;
import model.Product;

import java.io.*;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;
public class ClientUdpSender {
    private static final int TIMEOUT = 3000;

    public static Object sendCommand(BaseCommand command, InetAddress serverAdd, int port)
            throws ServerTimeoutException, IOException {
        try (DatagramSocket socket = new DatagramSocket()) {
            socket.setSoTimeout(TIMEOUT);

            // 序列化前打印对象信息
            System.out.println("[Client] Sending command: " + command.getClass().getName());
            if (command instanceof Add addCommand) {
                Product product = addCommand.getProduct();
                System.out.println("[Client] Product to send: " + addCommand.getProduct());
                if (product == null) {
                    throw new IOException("Product is null before sending");
                }
            }

            // 序列化
            ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
            ObjectOutputStream objectStream = new ObjectOutputStream(byteStream);
            objectStream.writeObject(command);
            byte[] data = byteStream.toByteArray();
            System.out.println("[Client] Serialized data length: " + data.length);

            if (data.length > 65507) {
                throw new IOException("Data exceeds UDP packet limit (65507 bytes)");
            }

            // 发送UDP数据包
            DatagramPacket packet = new DatagramPacket(data, data.length, serverAdd, port);
            socket.send(packet);

            // 接收响应（可选）
            byte[] buffer = new byte[4096];
            DatagramPacket responsePacket = new DatagramPacket(buffer, buffer.length);
            socket.receive(responsePacket);
            return new ObjectInputStream(
                    new ByteArrayInputStream(responsePacket.getData())
            ).readObject();

        } catch (SocketTimeoutException e) {
            throw new ServerTimeoutException("Server not responding within " + TIMEOUT + "ms.");
        } catch (ClassNotFoundException e) {
            throw new IOException("Response deserialization failed: " + e.getMessage());
        }
    }
}