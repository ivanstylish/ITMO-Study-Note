package server;

import common.utility.Commands;
import io.github.cdimascio.dotenv.Dotenv;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.hibernate.SessionFactory;
import org.hibernate.internal.SessionFactoryImpl;
import server.commands.*;
import server.handlers.CommandHandler;
import server.managers.AuthManager;
import server.managers.CommandManager;
import server.managers.PersistenceManager;
import server.network.UDPDatagramServer;
import server.repositories.ProductRepository;
import server.utils.HibernateUtil;

import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

/**
 * Server side of the application.
 */
public class App {
  public static final int PORT = 5432;

  public static final Logger logger = LogManager.getLogger("ServerLogger");
  public static Dotenv dotenv;

  public static void main(String[] args) {
    SessionFactoryImpl sessionFactory = (SessionFactoryImpl) getHibernateSessionFactory();
    var session = sessionFactory.openSession();
    Runtime.getRuntime().addShutdownHook(new Thread(sessionFactory::close));

    var persistenceManager = new PersistenceManager(sessionFactory);
    var authManager = new AuthManager(sessionFactory, dotenv.get("PEPPER"));

    var repository = new ProductRepository(persistenceManager);
    var commandManager = initializeCommandManager(repository, authManager);

    try {
      var server = new UDPDatagramServer(
        InetAddress.getLocalHost(),
        PORT,
        new CommandHandler(commandManager, authManager)
      );
      server.run();
    } catch (SocketException e) {
      logger.fatal("There was a socket error", e);
    } catch (UnknownHostException e) {
      logger.fatal("Unknown host", e);
    }
  }

  private static SessionFactory getHibernateSessionFactory() {
    loadEnv();
    var url = dotenv.get("DB_URL");
    var user = dotenv.get("DB_USER");
    var password = dotenv.get("DB_PASSWORD");

    if (url == null || url.isEmpty() || user == null || user.isEmpty() || password == null || password.isEmpty()) {
      System.out.println("В .env no data for connection to the database found in the file");
      System.exit(1);
    }

    return HibernateUtil.getSessionFactory(url, user, password);
  }

  private static CommandManager initializeCommandManager(ProductRepository repository, AuthManager authManager) {
    return new CommandManager() {{
      register(Commands.REGISTER, new Register(authManager));
      register(Commands.AUTHENTICATE, new Authenticate(authManager));
      register(Commands.HELP, new Help(this));
      register(Commands.INFO, new Info(repository));
      register(Commands.SHOW, new Show(repository));
      register(Commands.ADD, new Add(repository));
      register(Commands.UPDATE, new Update(repository));
      register(Commands.REMOVE_BY_ID, new RemoveById(repository));
      register(Commands.CLEAR, new Clear(repository));
      register(Commands.HEAD, new Head(repository));
      register(Commands.ADD_IF_MAX, new AddIfMax(repository));
      register(Commands.ADD_IF_MIN, new AddIfMin(repository));
      register(Commands.SUM_OF_PRICE, new SumOfPrice(repository));
      register(Commands.FILTER_BY_PRICE, new FilterByPrice(repository));
      register(Commands.SORT, new Sort(repository));
      register(Commands.COUNT_BY_UNIT_OF_MEASURE, new CountByUnitOfMeasure(repository));
      register(Commands.MAX_BY_CREATION_DATE, new MaxByCreationDate(repository));
    }};
  }

  private static void loadEnv() {
    var environmentFile = ".env.dev";
    var isProduction = System.getenv("PROD");
    if (isProduction != null && isProduction.equals("true")) {
      environmentFile = ".env";
    }

    dotenv = Dotenv.configure()
      .filename(environmentFile)
      .ignoreIfMalformed()
      .ignoreIfMissing()
      .load();
  }
}
