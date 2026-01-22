1) Привести пример работы с Redux Toolkit. Показать настройку “слайса”, проиллюстрировать использование на примере одного React компонента. По меньшей мере должно быть показано 2 action-a.

```
import React from "react";
import { Provider, useDispatch, useSelector } from "react-redux";
import { configureStore, createSlice } from "@reduxjs/toolkit";

// slice + 2 actions
const slice = createSlice({
  name: "c",
  initialState: { v: 0 },
  reducers: {
    inc: (s) => { s.v++; },
    dec: (s) => { s.v--; },
  },
});

const store = configureStore({ reducer: slice.reducer });

function Counter() {
  const v = useSelector((s) => s.v);
  const d = useDispatch();
  return (
    <div>
      <b>{v}</b>
      <button onClick={() => d(slice.actions.inc())}>+</button>
      <button onClick={() => d(slice.actions.dec())}>-</button>
    </div>
  );
}

export default function App() {
  return (
    <Provider store={store}>
      <Counter />
    </Provider>
  );
}
```

2)Интерфейс на Angular, реализующий воспроизведение видео. Можно проигрывать, нажимать стоп и листать вперёд/назад

```
@Component({
  selector: 'app-root',
  template: `
    <iframe #player width="560" height="315"
      src="https://www.youtube.com/embed/dQw4w9WgXcQ?enablejsapi=1"
      frameborder="0"></iframe>

    <div>
      <button (click)="play()">play</button>
      <button (click)="stop()">stop</button>
    </div>
  `,
})
export class Example {
  play() { console.log('play'); }
  stop() { console.log('stop'); }
}
```

3)Интерфейс на JSF, формирующий страницу ввода логина и пароля. Необходимо реализовать как поведение входа в систему, так и сброса пароля. При сбросе пароля требуется указать почту и ввести код подтверждения из сообщения, высланного на почту. Необходимо также привести код Managed bean-ов, используемых в facelets.

```
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:h="http://java.sun.com/jsf/html">
<h:body>
<h:form>

  <h:commandLink value="#{b.login ? 'Забыли пароль?' : 'Назад'}"
                 action="#{b.toggle}"/>

  <h:panelGroup rendered="#{b.login}">
    <h:inputText value="#{b.user}" />
    <h:inputSecret value="#{b.pass}" />
    <h:commandButton value="Войти" action="#{b.signIn}" />
  </h:panelGroup>

  <h:panelGroup rendered="#{!b.login}">
    <h:inputText value="#{b.email}" rendered="#{!b.sent}" />
    <h:commandButton value="Код" action="#{b.send}" rendered="#{!b.sent}" />

    <h:panelGroup rendered="#{b.sent}">
      <h:inputText value="#{b.code}" />
      <h:commandButton value="Сбросить" action="#{b.check}" />
    </h:panelGroup>
  </h:panelGroup>

</h:form>
</h:body>
</html>


import javax.faces.bean.ManagedBean;
import javax.faces.bean.SessionScoped;
import java.io.Serializable;

@ManagedBean(name="b")
@SessionScoped
public class Bean implements Serializable {

  public boolean login = true, sent = false;
  public String user, pass, email, code;

  private final String sentCode = "1234"; 

  public String toggle() {
    login = !login;
    sent = false;
    return null;
  }

  public String signIn() {
    System.out.println("LOGIN: " + user);
    return null;
  }

  public String send() {
    sent = true;
    System.out.println("CODE to " + email + ": " + sentCode);
    return null;
  }

  public String check() {
    System.out.println(sentCode.equals(code) ? "OK" : "BAD");
    return null;
  }
}
```

4)Интерфейс на Angular, формирующий страницу ввода логина и пароля. Необходимо реализовать как поведение входа в систему, так и сброса пароля. При сбросе пароля требуется указать почту и ввести код подтверждения из сообщения, высланного на почту.

```
import { Component } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule],
  template: `
    <button (click)="m=!m; s=false">{{m?'Сброс':'Вход'}}</button>

    @if(!m){
      <input placeholder="логин" [(ngModel)]="u">
      <input placeholder="пароль" type="password" [(ngModel)]="p">
      <button (click)="alert('Вход')">OK</button>
    } @else {
      @if(!s){
        <input placeholder="почта" [(ngModel)]="e">
        <button (click)="c='1234'; s=true; alert('Код отправлен: 1234')">Код</button>
      } @else {
        <input placeholder="код" [(ngModel)]="k">
        <button (click)="alert(k===c?'ОК':'Неверно')">Проверить</button>
      }
    }
})
class App {
  m=false; s=false; u=''; p=''; e=''; k=''; c='';
  alert(t:string){ window.alert(t); }
}

bootstrapApplication(App);
```

5)Интерфейс на Angular, реализующий чат-бота, который на любое сообщение отвечает словами «Сам дурак»

```
import { Component } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule],
  template: `
    <input [(ngModel)]="t"><button (click)="s()">OK</button>
    @for (m of a; track $index) { <div>{{m}}</div> }
  `
})
class App {
  t=''; a:string[]=[];
  s(){ if(!this.t.trim()) return; this.a.push(this.t,'Сам дурак'); this.t=''; }
}

bootstrapApplication(App);
```

6)Интерфейс на React, реализующий чат-бота, который на любое сообщение
отвечает словами «Сам дурак»
import { useState } from "react";

```
export default function App() {
  const [t, setT] = useState("");
  const [a, setA] = useState([]);

  const s = () => {
    if (!t.trim()) return;
    setA([...a, t, "Сам дурак"]);
    setT("");
  };

  return (
    <>
      <input value={t} onChange={(e) => setT(e.target.value)} />
      <button onClick={s}>OK</button>
      {a.map((m, i) => <div key={i}>{m}</div>)}
    </>
  );
}
```


7). Интерфейс на React, реализующий калькулятор с базовыми операциями над
двумя дробными числами: сложение, вычитание, умножение, деление. При
попытке деления на ноль должен выскакивать alert “Вы были отчислены”.

```
import { useState } from "react";

export default function App() {
  const [a, A] = useState("");
  const [b, B] = useState("");
  const [r, R] = useState("");

  const c = (o) => {
    const x = +a, y = +b;
    if (o === "/" && y === 0) return alert("Вы были отчислены");
    R(o === "+" ? x + y : o === "-" ? x - y : o === "*" ? x * y : x / y);
  };

  return (
    <>
      <input value={a} onChange={e => A(e.target.value)} />
      <input value={b} onChange={e => B(e.target.value)} />
      <button onClick={() => c("+")}>+</button>
      <button onClick={() => c("-")}>-</button>
      <button onClick={() => c("*")}>*</button>
      <button onClick={() => c("/")}>/</button>
      <div>{r}</div>
    </>
  );
}
```

8)Интерфейс на React, формирующий страницу ввода логина и пароля. Необходимо реализовать как поведение входа в систему, так и сброса пароля.
При сбросе пароля требуется указать почту и ввести код подтверждения
сообщения высланного на почту

```
import { useState } from "react";

export default function App() {
  const [m, setM] = useState(0);        
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [e, setE] = useState("");
  const [k, setK] = useState("");
  const [sent, setSent] = useState("");

  return (
    <>
      <button onClick={() => { setM(m ? 0 : 1); setK(""); }}>
        {m ? "Войти" : "Сброс"}
      </button>

      {!m ? (
        <>
          <input placeholder="логин" value={u} onChange={(x) => setU(x.target.value)} />
          <input placeholder="пароль" type="password" value={p} onChange={(x) => setP(x.target.value)} />
          <button onClick={() => alert("Вход выполнен")}>OK</button>
        </>
      ) : (
        <>
          {!sent ? (
            <>
              <input placeholder="почта" value={e} onChange={(x) => setE(x.target.value)} />
              <button onClick={() => { const c = "1234"; setSent(c); alert("Код отправлен: " + c); }}>
                Код
              </button>
            </>
          ) : (
            <>
              <input placeholder="код" value={k} onChange={(x) => setK(x.target.value)} />
              <button onClick={() => alert(k === sent ? "Код верный" : "Неверный код")}>
                Проверить
              </button>
            </>
          )}
        </>
      )}
    </>
  );
}
```

9)REST API на JAX-RS для отображения ленты новостей. Каждая новость
должна быть снабжена названием, описанием, изображением, датой. Должна
быть возможность создания новой новости, редактирования и удаления существующей

```
@Path("/news")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class NewsResource {

  @Inject
  private NewsService newsService;

  // Лента новостей
  @GET
  public Response getAll() {
    return Response.ok(newsService.getAll()).build();
  }

  // Одна новость
  @GET
  @Path("/{id}")
  public Response getById(@PathParam("id") Long id) {
    return Response.ok(newsService.getById(id)).build();
  }

  @POST
  public Response addNews(NewsDto newsDto) {
    News news = newsService.add(newsDto);
    return Response.status(Response.Status.CREATED).entity(news).build();
  }

  @PUT
  @Path("/{id}")
  public Response updateNews(@PathParam("id") Long id, NewsDto newsDto) {
    News news = newsService.update(id, newsDto);
    return Response.ok(news).build();
  }

  @DELETE
  @Path("/{id}")
  public Response deleteNews(@PathParam("id") Long id) {
    newsService.delete(id);
    return Response.noContent().build();
  }
}
```

10)REST API на JAX-RS предоставляющий интерфейс для бронирования и покупки авиабилетов. Требуется определить хотя бы 4 эндпоинта с различным
поведением

```
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;

@Path("/aviasales")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class AviasalesController {

  @GET
  public Response search() {
    return Response.ok("list of flights").build();
  }

  @POST
  public Response book(String ticket) {
    return Response.status(Response.Status.CREATED)
      .entity("booking created")
      .build();
  }

  @PUT
  @Path("/{id}/pay")
  public Response pay(@PathParam("id") Long id) {
    return Response.ok("ticket paid: " + id).build();
  }

  @DELETE
  @Path("/{id}")
  public Response cancel(@PathParam("id") Long id) {
    return Response.noContent().build();
  }
}
```

11)Интерфейс на JSF для отображения ленты новостей. Каждая новость должна быть снабжена названием, описание, изображение, датой. Должна быть
возможность создания новой новости. Список новостей должен являться
динамическим и браться из CDI бина.

```
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:h="http://xmlns.jcp.org/jsf/html"
      xmlns:f="http://xmlns.jcp.org/jsf/core"
      xmlns:ui="http://xmlns.jcp.orgjsf/facelets">
<h:body>

<ui:repeat value="#{newsService.newsList}" var="n">
  <h2>#{n.title}</h2>
  #{n.text}<br/>
  <img src="#{n.imgUrl}" width="200"/><br/>
  #{n.date}<hr/>
</ui:repeat>

<h:form>
  <h:inputText value="#{newsService.currentNewsTitle}" />
  <h:inputText value="#{newsService.currentNewsText}" />
  <h:inputText value="#{newsService.currentNewsImgUrl}" />
  <h:commandButton value="Добавить" action="#{newsService.addNewsToList}">
    <f:ajax render="@form"/>
  </h:commandButton>
</h:form>

</h:body>
</html>

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Named;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Named("newsService")
@ApplicationScoped
public class NewsService {

  public static class News {
    public String title, text, imgUrl;
    public LocalDateTime date;
    public News(String t,String x,String i){
      title=t; text=x; imgUrl=i; date=LocalDateTime.now();
    }
  }

  public List<News> newsList = new ArrayList<>();
  public String currentNewsTitle="", currentNewsText="", currentNewsImgUrl="";

  public void addNewsToList() {
    newsList.add(0, new News(
      currentNewsTitle,
      currentNewsText,
      currentNewsImgUrl
    ));
    currentNewsTitle=currentNewsText=currentNewsImgUrl="";
  }
}
```

12)Привести пример Java класса, использующего передаваемый через конструктор экземпляр JPA EntityManager, для реализации следующих операций со
студентами: зачисление(создание), редактирование персональной информации, отчисление(удаление), получение записи о студенте по идентификатору

```
import jakarta.persistence.EntityManager;
import static java.util.Objects.isNull;

public class StudentService {

  private EntityManager eManager;

  public StudentService(EntityManager eManager) {
    this.eManager = eManager;
  }

  public void create(Student student) {
    eManager.persist(student);
  }

  public Student read(Long studentId) {
    return eManager.find(Student.class, studentId);
  }

  public void update(Student student) {
    eManager.merge(student);
  }

  public void delete(Student student) {
    Student managed = read(student.getId());
    if (!isNull(managed)) eManager.remove(managed);
  }
}
```


13)Привести пример Java класса, использующего передаваемый через конструктор экземпляр JPA EntityManager, для реализации следующих операций со
студентами: зачисление(создание), редактирование персональной информации, отчисление(удаление), получение записи о студенте по идентификатору

```
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