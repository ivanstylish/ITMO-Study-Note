package server;

import model.Product;
import server.command.*;
import server.logging.ServerLogger;
import server.managers.CollectionManager;
import server.network.ServerUdpListener;

import java.io.IOException;

public class ServerMain {
    public static void main(String[] args) {
        try {
            String filePath = System.getenv("COLLECTION_FILE");
            if (filePath == null) {
                throw new IllegalArgumentException("Environment variable 'COLLECTION_FILE' is not set.");
            }

            CollectionManager manager = new CollectionManager(filePath);
            ServerCommandExecutor executor = new ServerCommandExecutor(manager, new Product());
            ServerUdpListener listener = new ServerUdpListener(executor, 5786);

            executor.registerCommand(new Add(manager, executor.getProduct()));
            executor.registerCommand(new AddIfMin(manager));
            executor.registerCommand(new Clear(manager));
            executor.registerCommand(new CountByUnitOfMeasure(manager));
            executor.registerCommand(new Help(executor));
            executor.registerCommand(new Info(manager));
            executor.registerCommand(new InsertAt(manager));
            executor.registerCommand(new MaxByCreationDate(manager));
            executor.registerCommand(new RemoveAnyByPrice(manager));
            executor.registerCommand(new RemoveById(manager));
            executor.registerCommand(new Show(manager));
            executor.registerCommand(new Sort(manager));
            executor.registerCommand(new Update(manager));

            listener.start();
            ServerLogger.logInfo(" ==== Server is starting ====");
        } catch (IOException e) {
            ServerLogger.logError("Server startup failure", e);
        }
    }
}
