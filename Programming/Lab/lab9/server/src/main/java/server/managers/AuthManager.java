package server.managers;

import com.google.common.hash.Hashing;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.logging.log4j.Logger;
import org.hibernate.SessionFactory;
import server.App;
import server.dao.UserDAO;

import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.List;

public class AuthManager {
  private final SessionFactory sessionFactory;
  private final int SALT_LENGTH = 10;
  private final String pepper;

  private final Logger logger = App.logger;

  public AuthManager(SessionFactory sessionFactory, String pepper) {
    this.sessionFactory = sessionFactory;
    this.pepper = pepper;
  }

  public int registerUser(String login, String password) {
    logger.info("Creating a new user " + login);

    var salt = generateSalt();
    var passwordHash = generatePasswordHash(password, salt);

    var dao = new UserDAO();
    dao.setName(login);
    dao.setPasswordDigest(passwordHash);
    dao.setSalt(salt);

    var session = sessionFactory.openSession();
    session.beginTransaction();
    session.persist(dao);
    session.getTransaction().commit();
    session.close();

    var newId = dao.getId();
    logger.info("User successfully created, id#" + newId);
    return newId;
  }

  public int authenticateUser(String login, String password) throws SQLException {
    logger.info("User authentication " + login);
    var session = sessionFactory.openSession();
    session.beginTransaction();

    var query = session.createQuery("SELECT u FROM users u WHERE u.name = :name");
    query.setParameter("name", login);

    List<UserDAO> result = (List<UserDAO>) query.list();

    if (result.isEmpty()) {
      logger.warn("Incorrect password for the user " + login);
      return 0;
    }

    var user = result.get(0);
    session.getTransaction().commit();
    session.close();

    var id = user.getId();
    var salt = user.getSalt();
    var expectedHashedPassword = user.getPasswordDigest();

    var actualHashedPassword = generatePasswordHash(password, salt);
    if (expectedHashedPassword.equals(actualHashedPassword)) {;
      logger.info("User " + login + " authenticated with id#" + id);
      return id;
    }

    logger.warn(
      "Incorrect password for the user " + login +
        ". Expected '" + expectedHashedPassword + "', received '" + actualHashedPassword + "'"
    );
    return 0;
  }

  private String generateSalt() {
    return RandomStringUtils.randomAlphanumeric(SALT_LENGTH);
  }

  private String generatePasswordHash(String password, String salt) {
    return Hashing.sha256()
      .hashString(pepper + password + salt, StandardCharsets.UTF_8)
      .toString();
  }
}
