package server.repositories;

import common.model.Coordinates;
import common.model.Organization;
import common.model.Product;
import common.exceptions.BadOwnerException;
import common.user.User;
import common.utility.ProductComparator;
import org.apache.logging.log4j.Logger;
import server.App;
import server.managers.PersistenceManager;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Queue;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;

/**
 * Operates the collection.
 */
public class ProductRepository {
  private final Logger logger = App.logger;

  private Queue<Product> collection = new PriorityQueue<>();
  private LocalDateTime lastInitTime;
  private LocalDateTime lastSaveTime;
  private final PersistenceManager persistenceManager;

  private final ReentrantLock lock = new ReentrantLock();

  public ProductRepository(PersistenceManager persistenceManager) {
    this.lastInitTime = null;
    this.lastSaveTime = null;
    this.persistenceManager = persistenceManager;

    try {
      load();
    } catch (Exception e) {
      logger.fatal("Error loading products from the database!", e);
      System.exit(3);
    }

    if(!validateAll()) {
      logger.fatal("Invalid products in the downloaded file!");
      System.exit(2);
    }
  }

  public boolean validateAll() {
    for(var product : new ArrayList<>(get())) {
      if (!product.validate()) {
        logger.warn("Product with id=" + product.getId() + " has invalid fields.");
        return false;
      }
      if (product.getManufacturer() != null) {
        if(!product.getManufacturer().validate()) {
          logger.warn("Manufacturer of the product with id=" + product.getId() + " has invalid fields.");
          return false;
        }
      }
    }
      logger.info("! Loaded products are valid.");
    return true;
  }

  /**
   * @return collection.
   */
  public Queue<Product> get() {
    return collection;
  }

  /**
   * @return Last Initialisation Time.
   */
  public LocalDateTime getLastInitTime() {
    return lastInitTime;
  }

  /**
   * @return Lately of preservation.
   */
  public LocalDateTime getLastSaveTime() {
    return lastSaveTime;
  }

  /**
   * @return Collection type name.
   */
  public String type() {
    return collection.getClass().getName();
  }

  /**
   * @return Collection size.
   */
  public int size() {
    return collection.size();
  }

  /**
   * @return First element of the collection (null if the collection is empty).
   */
  public Product first() {
    if (collection.isEmpty()) return null;
    return sorted().get(0);
  }

  /**
   * @return Sorted collection.
   */
  public List<Product> sorted() {
    return new ArrayList<>(collection)
      .stream()
      .sorted(new ProductComparator())
      .collect(Collectors.toList());
  }

  /**
   * @param id ID element.
   * @return Element by its ID or null if not found.
   */
  public Product getById(int id) {
    for (Product element : collection) {
      if (element.getId() == id) return element;
    }
    return null;
  }

  /**
   * @param id ID element.
   * @return Checks if an element with this ID exists.
   */
  public boolean checkExist(int id) {
    return getById(id) != null;
  }

  /**
   * Adds a product to the collection
   * @param element Element to add.
   * @return id new element
   */
  public int add(User user, Product element) {
    var newId = persistenceManager.add(user, element);
    logger.info("New product added to the database.");

    lock.lock();
    collection.add(element.copy(newId, user.withoutPassword()));
    lastSaveTime = LocalDateTime.now();
    lock.unlock();

    logger.info("Product added!");

    return newId;
  }

  /**
   * Updates an item in the collection.
   * @param user User.
   * @param element Renewal element.
   */
  public void update(User user, Product element) throws BadOwnerException {
    var product = getById(element.getId());
    if (product == null) {
      add(user, element);
    } else if (product.getCreatorId() == user.getId()) {
      logger.info("Product Update id#" + product.getId() + " in the database.");

      var orgId = persistenceManager.update(user, element);

      lock.lock();
      if (orgId != -1) element.getManufacturer().setId(orgId);
      getById(element.getId()).update(element);
      lastSaveTime = LocalDateTime.now();
      lock.unlock();

      logger.info("The product has been successfully updated!");
    } else {
      logger.warn("Other owner. Exception.");
      throw new BadOwnerException();
    }
  }

  /**
   * Deletes a product from the collection.
   * @param id Product ID of the item to be deleted.
   * @return number of deleted products.
   */
  public int remove(User user, int id) throws BadOwnerException {
    if (getById(id).getCreatorId() != user.getId()) {
      logger.warn("Other owner. Exception.");
      throw new BadOwnerException();
    }

    var removedCount = persistenceManager.remove(user, id);
    if (removedCount == 0) {
      logger.warn("Nothing has been deleted.");
      return 0;
    }

    lock.lock();
    collection.removeIf(product -> product.getId() == id && product.getCreatorId() == user.getId());
    lastSaveTime = LocalDateTime.now();
    lock.unlock();

    return removedCount;
  }

  /**
   * Cleans up the collection.
   */
  public void clear(User user) {
    persistenceManager.clear(user);

    lock.lock();
    collection.removeIf(product -> product.getCreatorId() == user.getId());
    lastSaveTime = LocalDateTime.now();
    lock.unlock();
  }

  /**
   * Loads a collection from the database.
   */
  private void load() {
    logger.info("Download started...");

    lock.lock();
    collection = new PriorityQueue<>();
    var daos = persistenceManager.loadProducts();

    var products = daos.stream().map((dao) -> {
      Organization manufacturer = null;
      if (dao.getManufacturer() != null) {
        manufacturer = new Organization(
          dao.getManufacturer().getId(),
          dao.getManufacturer().getName(),
          dao.getManufacturer().getEmployeesCount(),
          dao.getManufacturer().getType()
        );
      }
      return new Product(
        dao.getId(),
        dao.getName(),
        new Coordinates(dao.getX(), dao.getY()),
        dao.getCreationDate(),
        dao.getPrice(),
        dao.getUnitOfMeasure(),
        manufacturer,
        new User(dao.getCreator().getId(), dao.getCreator().getName(), "")
      );
    }).toList();

    collection.addAll(products);
    lastInitTime = LocalDateTime.now();
    lock.unlock();

    logger.info("Download complete!");
  }

  @Override
  public String toString() {
    if (collection.isEmpty()) return "The collection is empty!";

    var info = new StringBuilder();
    for (Product product : collection) {
      info.append(product);
      info.append("\n\n");
    }
    return info.substring(0, info.length() - 2);
  }
}
