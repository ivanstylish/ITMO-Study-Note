import dao.ProductDAO;
import db.DatabaseInitializer;
import model.Product;
import network.RequestHandler;

import network.UDPChannelManager;

import java.io.IOException;
import java.sql.SQLException;

import java.util.concurrent.ConcurrentHashMap;

public class ServerMain {
    private static final int PORT = 5432;
    protected ConcurrentHashMap<Long, Product> products;

    public static void main(String[] args) throws SQLException {
        try {
            new ServerMain().start();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void start() throws SQLException, IOException {
        DatabaseInitializer.init();
        ProductDAO productDAO = new ProductDAO();
        products = productDAO.loadAllProducts();

        RequestHandler requestHandler = new RequestHandler(productDAO);

        try {
            UDPChannelManager channelManager = new UDPChannelManager(PORT, requestHandler);
            channelManager.start();
        } catch (IOException e) {
            throw new RuntimeException("Network initialization failed", e);
        }
    }
}