import auth.AuthService;
import commands.CommandProcessor;
import dao.CoordinatesDAO;
import dao.OrganizationDAO;
import dao.ProductDAO;
import dao.UserDAO;
import db.DatabaseConnector;
import db.DatabaseInitializer;
import logger.Logger;
import network.RequestHandler;
import network.UDPChannelManager;

import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLException;

public class ServerMain {
    private static final int PORT = 5432;

    public static void main(String[] args) throws SQLException {
        try {
            new ServerMain().start();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void start() throws SQLException, IOException {
        Logger.info("Initializing server...");
        DatabaseInitializer.init();

        CommandProcessor commandProcessor = getCommandProcessor();

        RequestHandler requestHandler = new RequestHandler(commandProcessor);

        try {
            UDPChannelManager channelManager = new UDPChannelManager(PORT, requestHandler);
            Logger.info("Server started on port " + PORT);
            channelManager.start();
        } catch (IOException e) {
            throw new RuntimeException("Network initialization failed", e);
        }
    }

    private static CommandProcessor getCommandProcessor() throws SQLException {
        Connection connection = DatabaseConnector.getConnection();

        ProductDAO productDAO = new ProductDAO();
        OrganizationDAO organizationDAO = new OrganizationDAO();
        CoordinatesDAO coordinatesDAO = new CoordinatesDAO();
        UserDAO userDAO = new UserDAO(connection);
        AuthService authService = new AuthService(userDAO);


        return new CommandProcessor(
                null,
                authService,
                organizationDAO,
                coordinatesDAO,
                productDAO,
                productDAO.loadAllProducts()
        );
    }
}