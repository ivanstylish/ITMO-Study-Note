package client;

import client.exception.InvalidCommandException;
import client.exception.ServerTimeoutException;
import client.network.ClientUdpSender;
import client.parsers.ClientCommandParser;
import client.util.ClientConsole;
import client.command.BaseCommand;
import client.util.InputHandler;


import java.io.*;
import java.net.*;

public class ClientMain {
    private static final String SERVER_HOST = "localhost";
    private static final int SERVER_PORT = 5786;
    private static final int TIMEOUT_MS = 3000;

    public static void main(String[] args) {
        ClientConsole console = new ClientConsole();
        InputHandler inputHandler = new InputHandler(console);
        ClientCommandParser parser = new ClientCommandParser(inputHandler);

        console.printSuccess("=== Welcome to Varnothing's client ===");
        console.printSuccess("=== PLEASE ENTER WHAT YOU WANT ===");

        try(DatagramSocket socket = new DatagramSocket()) {
            socket.setSoTimeout(TIMEOUT_MS);
            InetAddress serverAddress = InetAddress.getByName(SERVER_HOST);

            while (true) {
                String input = console.readLine("");
                if (input.equalsIgnoreCase("exit")) break;

                try {
                    BaseCommand command = parser.parse(input);
                    Object response = ClientUdpSender.sendCommand(command, serverAddress, SERVER_PORT);

                    if (response != null) {
                        console.printResult(response.toString());
                    } else {
                        console.printError("Server returned null response");
                    }
                } catch (InvalidCommandException e) {
                    console.printError(e.getMessage());
                } catch (ServerTimeoutException e) {
                    console.printError("Server timeout: " + e.getMessage());
                } catch (IOException e) {
                    console.printError("Network error: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            console.printError("Client startup failure: " + e.getMessage());
        }
    }
}