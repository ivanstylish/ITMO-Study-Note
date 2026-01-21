### 1. Задание: Реализовать интерфейс на JSF для отображения ленты новостей. Каждая новость должна быть снабжена названием, описанием, изображением и датой. Должна быть возможность создания новой новости. Список новостей должен являться динамическим и браться из CDI бина.
  1. 实体
```java
import jakarta.enterprise.context.ApplicationScoped;
import java.io.Serializable;
import java.time.LocalDate;

@ApplicationScoped
public class News implements Serializable {
    private Long id;
    private String title;
    private String description;
    private String imageUrl; // URL изображения
    private LocalDate date;

    // Конструкторы
    public News() {}

    public News(String title, String description, String imageUrl) {
        this.title = title;
        this.description = description;
        this.imageUrl = imageUrl;
        this.date = LocalDate.now();
    }

    // Геттеры и сеттеры
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }

    public LocalDate getDate() { return date; }
    public void setDate(LocalDate date) { this.date = date; }
}
```

  2. 用于存储和管理新闻的 CDI bean
```java
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Named;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

@Named
@ApplicationScoped
public class NewsService {
    private final List<News> newsList = new ArrayList<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    // Получить все новости (динамический список)
    public List<News> getAllNews() {
        return newsList;
    }

    // Добавить новую новость
    public void addNews(News news) {
        news.setId(idGenerator.getAndIncrement());
        newsList.add(0, news); // Добавляем в начало ленты
    }
}
```

  3. 表单的托管 bean
```java
import jakarta.enterprise.context.RequestScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;

@Named
@RequestScoped
public class NewsBean {
    @Inject
    private NewsService newsService;

    private String title;
    private String description;
    private String imageUrl;

    // Метод для создания новости
    public String createNews() {
        News news = new News(title, description, imageUrl);
        newsService.addNews(news);
        // Очистка формы
        title = null;
        description = null;
        imageUrl = null;
        return "news?faces-redirect=true"; // Переход обратно на страницу
    }

    // Геттеры и сеттеры
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
}
```

  4. 页面html
```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:h="jakarta.faces.html"
      xmlns:f="jakarta.faces.core">
<h:head>
    <title>Лента новостей</title>
</h:head>
<h:body>
    <h1>Лента новостей</h1>

    <!-- Форма создания новости -->
    <h:form>
        <h:panelGrid columns="2">
            <h:outputLabel value="Заголовок:" for="title"/>
            <h:inputText id="title" value="#{newsBean.title}" required="true"/>

            <h:outputLabel value="Описание:" for="description"/>
            <h:inputTextarea id="description" value="#{newsBean.description}" required="true"/>

            <h:outputLabel value="URL изображения:" for="imageUrl"/>
            <h:inputText id="imageUrl" value="#{newsBean.imageUrl}" required="true"/>

            <h:commandButton value="Добавить новость" action="#{newsBean.createNews}"/>
        </h:panelGrid>
    </h:form>

    <hr/>

    <!-- Динамический список новостей из CDI бина -->
    <h:dataTable value="#{newsService.allNews}" var="news">
        <h:column>
            <f:facet name="header">Новость</f:facet>
            <h:panelGrid columns="1">
                <h:outputText value="#{news.title}" style="font-weight: bold; font-size: 1.2em"/>
                <h:graphicImage url="#{news.imageUrl}" width="300"/>
                <h:outputText value="#{news.description}"/>
                <h:outputText value="#{news.date}" style="font-style: italic; color: gray"/>
            </h:panelGrid>
        </h:column>
    </h:dataTable>
</h:body>
</html>
```

### 2. Интерфейс на React, реализующий калькулятор с базовыми операциями над двумя дробными числами: сложение, вычитание, умножение, деление. При попытке деления на ноль должен выскакивать alert “Вы были отчислены”.
``` Java
import React, { useState } from 'react';

const Calculator = () => {
  const [firstNumber, setFirstNumber] = useState(0);
  const [secondNumber, setSecondNumber] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleOperation = (operation) => {
    const num1 = parseFloat(firstNumber);
    const num2 = parseFloat(secondNumber);

    if (operation === '/' && num2 === 0) {
      setError('Вы были отчислены');
      setResult(null);
      return;
    }

    setError(null);

    let res;
    switch (operation) {
      case '+':
        res = num1 + num2;
        break;
      case '-':
        res = num1 - num2;
        break;
      case '*':
        res = num1 * num2;
        break;
      case '/':
        res = num1 / num2;
        break;
      default:
        res = 0;
    }

    setResult(res);
  };

  return (
    <div>
      <input
        type="number"
        value={firstNumber}
        onChange={(e) => setFirstNumber(e.target.value)}
        placeholder="Первое число"
      />
      <input
        type="number"
        value={secondNumber}
        onChange={(e) => setSecondNumber(e.target.value)}
        placeholder="Второе число"
      />
      <button onClick={() => handleOperation('+')}>+</button>
      <button onClick={() => handleOperation('-')}>-</button>
      <button onClick={() => handleOperation('*')}>*</button>
      <button onClick={() => handleOperation('/')}>/</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result !== null && !error && <p>Результат: {result}</p>}
    </div>
  );
};

export default Calculator;
```

### 3. Привести пример Java класса, использующего передаваемый через конструктор экземпляр JPA EntityManager, для реализации следующих операций со студентами: создание (сохранение), редактирование персональной информации, отчисление (удаление), получение записи о студенте по идентификатору.
(Открытый вопрос — пример кода)
Пример правильного ответа (Repository-класс):

```java
import jakarta.persistence.EntityManager;

public class StudentRepository {
    private final EntityManager em;

    public StudentRepository(EntityManager em) {
        this.em = em;
    }

    public void create(Student student) {
        em.persist(student);
    }

    public void updatePersonalInfo(Student student) {
        em.merge(student);
    }

    public void delete(Student student) {
        em.remove(student);
    }

    public Student findById(int id) {
        return em.find(Student.class, id);
    }
}
```