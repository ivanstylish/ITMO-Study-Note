package server.managers;

import common.domain.*;
import common.user.User;
import org.apache.logging.log4j.Logger;

import org.hibernate.SessionFactory;
import server.App;
import server.dao.OrganizationDAO;
import server.dao.ProductDAO;
import server.dao.UserDAO;

import java.util.*;

public class PersistenceManager {
  private final SessionFactory sessionFactory;
  private final Logger logger = App.logger;

  public PersistenceManager(SessionFactory sessionFactory) {
    this.sessionFactory = sessionFactory;
  }

  public int add(User user, Product product) {
    logger.info("Adding a new product " + product.getName());
    OrganizationDAO newOrg = null;
    if (product.getManufacturer() != null) {
      newOrg = addOrganization(user, product.getManufacturer());
    }

    var dao = new ProductDAO(product);
    dao.setManufacturer(newOrg);
    dao.setCreator(new UserDAO(user));

    var session = sessionFactory.openSession();
    session.beginTransaction();
    session.persist(dao);
    session.getTransaction().commit();
    session.close();

    logger.info("Adding a product has been successfully completed.");

    var newId = dao.getId();
    logger.info("The new product id is " + newId);
    return newId;
  }

  public OrganizationDAO addOrganization(User user, Organization organization) {
    logger.info("Adding a new organisation " + organization.getName());

    var dao = new OrganizationDAO(organization);
    dao.setCreator(new UserDAO(user));

    var session = sessionFactory.openSession();
    session.beginTransaction();
    session.persist(dao);
    session.getTransaction().commit();

    logger.info("Adding an organisation has been successfully completed.");

    logger.info("The new organisation id is " + dao.getId());
    return dao;
  }

  public int update(User user, Product product) {
    logger.info("Product update id#" + product.getId());
    var session = sessionFactory.openSession();

    session.beginTransaction();
    var productDAO = session.get(ProductDAO.class, product.getId());

    int ordDaoId = -1;
    if (product.getManufacturer() != null) {
      ordDaoId = updateOrganization(user, product.getManufacturer()).getId();
    } else {
      productDAO.setManufacturer(null);
    }
    productDAO.update(product);
    session.update(productDAO);

    session.getTransaction().commit();
    session.close();
    logger.info("The product update has been completed!");

    return ordDaoId;
  }

  public OrganizationDAO updateOrganization(User user, Organization organization) {
    logger.info("Organization update id#" + organization.getId());

    var session = sessionFactory.openSession();
    session.beginTransaction();
    var organizationDAO = session.get(OrganizationDAO.class, organization.getId());
    organizationDAO.update(organization);

    session.update(organizationDAO);
    session.getTransaction().commit();
    session.close();
    logger.info("Organisational renewal completed!");

    return organizationDAO;
  }

  public void clear(User user) {
    logger.info("Purification of the user's products id#" + user.getId() + " from the database.");

    var session = sessionFactory.openSession();
    session.beginTransaction();
    var query = session.createQuery("DELETE FROM products WHERE creator.id = :creator");
    query.setParameter("creator", user.getId());
    var deletedSize = query.executeUpdate();
    session.getTransaction().commit();
    session.close();
    logger.info("Deleted " + deletedSize + " products.");
  }

  public int remove(User user, int id) {
    logger.info("Product removal №" + id + " user id#" + user.getId() + ".");

    var session = sessionFactory.openSession();
    session.beginTransaction();

    var query = session.createQuery("DELETE FROM products WHERE creator.id = :creator AND id = :id");
    query.setParameter("creator", user.getId());
    query.setParameter("id", id);

    var deletedSize = query.executeUpdate();
    session.getTransaction().commit();
    session.close();
    logger.info("Deleted " + deletedSize + " products.");

    return deletedSize;
  }

  public List<ProductDAO> loadProducts() {
    var session = sessionFactory.openSession();
    session.beginTransaction();

    var cq = session.getCriteriaBuilder().createQuery(ProductDAO.class);
    var rootEntry = cq.from(ProductDAO.class);
    var all = cq.select(rootEntry);

    var result = session.createQuery(all).getResultList();
    session.getTransaction().commit();
    session.close();
    return result;
  }
}
