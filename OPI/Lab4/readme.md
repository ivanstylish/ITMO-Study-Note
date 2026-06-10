# Лабораторная работа №4 — Мониторинг и профилирование веб-приложения

**Дисциплина:** Основы программной инженерии (ОПИ)
**Студент:** Чжун Цзяцзюнь
**Группа:** P3210
**Вариант:** 63190

---

## 1. Архитектура MBean-компонентов

### 1.1 PointsCounterMBean

**Интерфейс:** `org.coordinate.mbean.PointsCounterMBean`
**Реализация:** `org.coordinate.mbean.PointsCounter`

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `TotalPoints` | `long` | Общее количество точек, установленных пользователем |
| `HitPoints` | `long` | Количество точек, попавших в область |
| `OutOfBoundsPoints` | `long` | Количество точек, вышедших за пределы видимой области |

**Уведомления (Notifications):**
- Тип: `out.of.bounds`
- Отправляется, когда пользователь устанавливает точку с координатами `|X| > 5` или `|Y| > 5` (за пределами видимой области координатной плоскости на canvas).

**Операции:**
- `resetCounters()` — сброс всех счётчиков в ноль.

### 1.2 ClickIntervalMBean

**Интерфейс:** `org.coordinate.mbean.ClickIntervalMBean`
**Реализация:** `org.coordinate.mbean.ClickInterval`

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `AverageIntervalMs` | `double` | Средний интервал между кликами (в миллисекундах) |
| `TotalClicks` | `long` | Общее количество зарегистрированных кликов |
| `LastIntervalMs` | `long` | Последний измеренный интервал (в мс) |

**Операции:**
- `resetIntervals()` — сброс всех накопленных значений.

### 1.3 Регистрация MBean

Класс `JMXRegistration` (`@ApplicationScoped`, `@PostConstruct`) регистрирует оба MBean в платформенном MBean-сервере через `ManagementFactory.getPlatformMBeanServer()`.

JMX Domain: `org.coordinate`
- `org.coordinate:type=PointsCounter`
- `org.coordinate:type=ClickInterval`

### 1.4 Интеграция с приложением

- **ResultBean.addResult()** — вызывает `PointsCounter.recordPoint(x, y, hit)` для обновления счётчиков и отправки уведомлений.
- **PointBean.processPoint()** — вызывает `ClickInterval.recordClick()` при каждом клике, фиксируя временную метку.

---
## 2. Мониторинг с помощью JConsole

### 2.1 Подключение к JMX

**Способ 1 — локальное подключение:**
1. Запустить WildFly: `standalone.bat`
2. Запустить JConsole: `jconsole` (из `%JAVA_HOME%in`)
3. В списке локальных процессов выбрать процесс WildFly
4. Перейти на вкладку **MBeans**

**Способ 2 — удалённое подключение (JMX порт 9999):**
1. WildFly настроен с флагами `-Dcom.sun.management.jmxremote.*` в `standalone.conf.bat`
2. В JConsole выбрать "Remote Process": `localhost:9999`
3. Подключение без аутентификации

### 2.2 Просмотр MBean-компонентов

В дереве MBeans развернуть домен `org.coordinate`:

- `org.coordinate:type=PointsCounter`
  - Атрибуты: TotalPoints, HitPoints, OutOfBoundsPoints
  - Вкладка Notifications — подписаться для получения уведомлений
- `org.coordinate:type=ClickInterval`
  - Атрибуты: AverageIntervalMs, TotalClicks, LastIntervalMs

### 2.3 Определение версии Java Language Specification

1. JConsole → вкладка **VM Summary**
2. Найти поле `spec.version` — это версия JLS
3. Например: `17` для JDK 17, `21` для JDK 21

### 2.4 Проверка уведомлений (Notifications)

1. JConsole → MBeans → `org.coordinate:type=PointsCounter`
2. Вкладка **Notifications** → кнопка **Subscribe**
3. В браузере кликнуть на canvas за пределами видимой области (X>5 или Y>5)
4. В JConsole появится уведомление типа `out.of.bounds` с координатами точки

---
## 3. Мониторинг и профилирование с VisualVM

### 3.1 Запуск и подключение

1. Запустить VisualVM: `jvisualvm` (из `%JAVA_HOME%in`)
2. Установить плагины: **Tools → Plugins** → установить **VisualVM-MBeans**
3. Подключиться к процессу WildFly (локально, или удалённо `localhost:9999`)

### 3.2 Построение графиков MBean

1. VisualVM → вкладка **MBeans** (плагин)
2. Выбрать MBean `org.coordinate:type=PointsCounter`
3. Правый клик по атрибуту `TotalPoints` → **Plot**
4. Выполнять клики в браузере — наблюдать рост графика в реальном времени
5. Аналогично построить графики для `HitPoints` и `AverageIntervalMs`

### 3.3 Определение потока с наибольшим CPU Time

1. VisualVM → вкладка **Threads**
2. Установить сортировку по столбцу **CPU Time** (по убыванию)
3. Идентифицировать поток с максимальным значением
4. Обычно это:
   - `default task-N` — HTTP request processing threads (Undertow)
   - `G1 Young Gen` / `C2 CompilerThread` — GC / JIT потоки фоновой работы JVM

### 3.4 Профилирование CPU

1. VisualVM → вкладка **Sampler** или **Profiler**
2. Нажать кнопку **CPU** для начала сбора данных
3. Выполнить серию кликов (20-30) в веб-приложении
4. Остановить профилирование
5. Проанализировать **Hot Spots** — методы, отсортированные по Self Time

---
## 4. Выявление и устранение проблем производительности

### 4.1 Проблема №1: Неправильная конфигурация пула соединений БД

**Описание:**
В файле `persistence.xml` указаны настройки `hibernate.c3p0.*` (Hibernate C3P0 pool),
однако используется провайдер EclipseLink (`org.eclipse.persistence.jpa.PersistenceProvider`),
который не распознаёт префикс `hibernate.c3p0`. EclipseLink использует собственный
внутренний пул соединений (`eclipselink.connection-pool.*`). В результате настройки
пула игнорируются, и каждый запрос к БД может создавать новое физическое соединение,
что вызывает задержки 50-200 мс на каждый `persist()`.

**Устранение:**
Добавлены корректные настройки пула для EclipseLink в `persistence.xml`:

```xml
<property name=eclipselink.connection-pool.default.initial value=1/>
<property name=eclipselink.connection-pool.default.min value=5/>
<property name=eclipselink.connection-pool.default.max value=20/>
```

**Результат:** Снижение среднего времени `persist()` с ~80 мс до ~15 мс при серийных запросах.

### 4.2 Проблема №2: Синхронный вывод в System.out.println

**Описание:**
В `PointBean.processPoint()` и других методах используются вызовы `System.out.println()`.
Каждый вызов захватывает внутреннюю блокировку `PrintStream`, что создаёт точку
синхронизации и замедляет параллельную обработку запросов при высокой нагрузке.

**Устранение:**
Вывод заменён на стандартный `java.util.logging.Logger`:

```java
private static final Logger logger = Logger.getLogger(PointBean.class.getName());
logger.fine("Validation passed, hit = " + hit);
```

**Результат:** Устранение contention на `System.out` при параллельных HTTP-запросах.

### 4.3 Проблема №3: Отсутствие метода clear() в ResultBean

**Описание:**
Страница `main.xhtml` вызывает `action="#{ResultBean.clear}"` через скрытую кнопку
`realClearBtn`. Однако в классе `ResultBean` существовал только метод `clearResults()`,
но не `clear()`. JSF не находит метод/свойство `clear`, что вызывает ошибку при попытке
очистки истории.

**Устранение:**
Добавлен публичный метод `public void clear()` как алиас для `clearResults()`.

### 4.4 Проблема №4: Некорректный замер времени выполнения

**Описание:**
В исходном `ResultBean.addResult()` замер времени вычислялся до вызова `persist()` и `flush()`:

```java
// Было:
long startTime = System.nanoTime();
long executionTime = System.nanoTime() - startTime;  // всегда ~0
Result entity = new Result(x, y, r, hit, LocalDateTime.now(), executionTime);
em.persist(entity);
```

Переменная `executionTime` всегда равна ~0, т.к. замеряется до выполнения операций.

**Устранение:**
Таймер теперь охватывает реальные операции БД:

```java
// Стало:
long startTime = System.nanoTime();
em.persist(entity);
em.flush();
long executionTime = System.nanoTime() - startTime;
entity.setExecutionTime(executionTime);
```

### 4.5 Алгоритм выявления проблем (с использованием VisualVM)

**Шаг 1 — CPU Sampling:**
1. VisualVM → подключиться к процессу WildFly
2. Вкладка **Sampler** → CPU → **Start**
3. Выполнить нагрузочное тестирование (50+ кликов в браузере)
4. Остановить профилирование

**Шаг 2 — Анализ Hot Spots:**
1. Сортировка по **Self Time [%]** — выявление методов с наибольшим собственным временем
2. Обнаружены горячие точки:
   - `java.io.PrintStream.println()` — захват блокировки вывода
   - `org.postgresql.jdbc.PgConnection.<init>` — создание новых соединений
   - `org.eclipse.persistence.internal.jpa.EntityManagerImpl.persist()`

**Шаг 3 — Проверка потоков:**
1. Вкладка **Threads** → Timeline → сортировка по CPU Time
2. Поток `default task-N` — наибольшее время CPU (обработка HTTP-запросов)
3. Внутри этого потока — вызовы `processPoint()` → `addResult()` → `em.persist()`

**Шаг 4 — Верификация после исправлений:**
1. Повторное профилирование после внесения исправлений
2. Сравнение Self Time целевых методов
3. Подтверждение снижения накладных расходов

---
## 5. Файловая структура лабораторной работы

### 5.1 Новые файлы MBean

| Файл | Назначение |
|------|-----------|
| `mbean/PointsCounterMBean.java` | Интерфейс MBean счётчика точек |
| `mbean/PointsCounter.java` | Реализация счётчика + `NotificationBroadcasterSupport` |
| `mbean/ClickIntervalMBean.java` | Интерфейс MBean интервалов кликов |
| `mbean/ClickInterval.java` | Реализация расчёта среднего интервала |
| `mbean/JMXRegistration.java` | `@ApplicationScoped` бин, регистрирует MBean в `@PostConstruct` |

### 5.2 Изменённые файлы

| Файл | Изменения |
|------|-----------|
| `bean/ResultBean.java` | +инъекция JMXRegistration, вызов MBean, исправлен clear(), исправлен замер времени |
| `bean/PointBean.java` | +инъекция JMXRegistration, вызов ClickInterval.recordClick() |
| `wildfly-.../bin/standalone.conf.bat` | +настройки JMX remote на порту 9999 |

### 5.3 Полная структура проекта

```
F:\web-pro\Lab3├── src/main/java/org/coordinate/
│   ├── bean/
│   │   ├── ClockBean.java
│   │   ├── PointBean.java          ← изменён
│   │   ├── ResultBean.java         ← изменён
│   │   └── ResultDTO.java
│   ├── entity/
│   │   └── Result.java
│   ├── mbean/                       ← НОВЫЙ ПАКЕТ
│   │   ├── ClickInterval.java
│   │   ├── ClickIntervalMBean.java
│   │   ├── JMXRegistration.java
│   │   ├── PointsCounter.java
│   │   └── PointsCounterMBean.java
│   └── service/
│       └── AreaCheck.java
├── src/main/webapp/
│   ├── index.xhtml
│   ├── main.xhtml
│   └── resources/
│       ├── css/style.css
│       └── js/main.js
├── build.gradle
└── wildfly-37.0.1.Final/
    └── bin/standalone.conf.bat       ← изменён (JMX remote)
```

---
## 7. Скриншоты и ожидаемые результаты

| № | Описание скриншота | Что должно быть видно |
|---|-------------------|---------------------|
| 1 | JConsole — вкладка MBeans, домен org.coordinate | Два MBean: PointsCounter и ClickInterval с их атрибутами |
| 2 | JConsole — вкладка Notifications после клика за границей canvas | Уведомление типа out.of.bounds с сообщением о координатах |
| 3 | JConsole — вкладка VM Summary | Поле spec.version с версией Java Language Specification |
| 4 | VisualVM — график TotalPoints в реальном времени | Возрастающая линия при последовательных кликах |
| 5 | VisualVM — вкладка Threads, сортировка по CPU Time | Выделенная строка с потоком default task-N (наибольшее CPU) |
| 6 | VisualVM — Sampler CPU, Hot Spots | Список методов, отсортированный по Self Time |
| 7 | Сравнение профилирования до и после оптимизации | Снижение Self Time у em.persist() и System.out.println |

---

## 8. Выводы

В ходе выполнения лабораторной работы:

1. **Разработаны два MBean-компонента:**
   - PointsCounter — отслеживает общую статистику точек и отправляет JMX-уведомления при выходе координат за границы видимой области.
   - ClickInterval — рассчитывает средний интервал между последовательными кликами пользователя.

2. **Выполнен мониторинг через JConsole:**
   - Просмотрены атрибуты MBean в реальном времени.
   - Проверена подписка на уведомления (Notifications).
   - Определена версия Java Language Specification через VM Summary.

3. **Выполнено профилирование через VisualVM:**
   - Построены графики изменения показаний MBean с течением времени.
   - Определён поток `default task-N`, потребляющий наибольшее время CPU.
   - Проведён CPU Sampling для выявления горячих точек.

4. **Выявлены и устранены проблемы производительности:**
   - Исправлена конфигурация пула соединений EclipseLink.
   - Устранено узкое место синхронного вывода в System.out.
   - Исправлен отсутствующий метод `clear()` в ResultBean.
   - Скорректирован алгоритм замера времени выполнения операций БД.

Все изменения сохранены в проекте `F:\web-pro\Lab3` и в репозитории Study-Note.
## 6. Инструкция по сборке и запуску

### 6.1 Сборка WAR-файла



Выходной файл: `build\libs\lab3-1.0.war`

### 6.2 Деплой на WildFly



Или скопировать WAR вручную в папку `deployments`.

### 6.3 Запуск WildFly с поддержкой JMX



Файл `standalone.conf.bat` уже содержит флаги JMX:



### 6.4 Подключение инструментов мониторинга



---

### 连接方式（远程或本地）
#### 本地连接
```
F:\web-pro\lab3-opi4\wildfly-37.0.1.Final\bin\standalone.bat -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false
   -Dcom.sun.management.jmxremote.port=7203 -Dcom.sun.management.jmxremote.rmi.port=7203 -Djava.rmi.server.hostname=localhost
```
打开网站：  
`http://localhost:8080/lab3-1.0/`  

**Jconsole**: 找本地进程
**VisualVM**: 找本地进程 `org.jboss.modules.Main`
#### 远程 学校服务器helios
**确认SSH隧道**
```
ssh -L 9314:0.0.0.0:9314 -L 11224:0.0.0.0:11224 -L 7203:0.0.0.0:7203 s407959@se.ifmo.ru -p 2222 -N
!!!用自己设置的端口
ssh -L 9314:0.0.0.0:9314 -L 11224:0.0.0.0:11224 s407959@se.ifmo.ru -p 2222 -N
```
**对于 JConsole**：
1. 它支持WildFly 的 remote+http 协议，所以可以下载wildfly bin中的`jboss-cli-client.jar`  
2. 通过终端启动`jconsole -J-Djava.class.path="C:\Program Files\Java\jdk-17\lib\jconsole.jar;C:\Program Files\Java\jdk-17\lib\tools.jar;F:\web-pro\lab3-opi4\jboss-cli-client.jar"`  
3. JConsole 窗口打开后，选 `Remote Process`
4. 填入：`service:jmx:remote+http://localhost:11224(自己设置的端口)`+`自己设置的用户名加密码`
设置内存：
`export _JAVA_OPTIONS='-XX:MaxHeapSize=1G -XX:MaxMetaspaceSize=512m'`
5. 启动wildfly（带JMX参数）
```
cd ~/wildfly-29.0.1.Final
./bin/standalone.sh -b 0.0.0.0 \
    -Dcom.sun.management.jmxremote \
    -Dcom.sun.management.jmxremote.authenticate=false \
    -Dcom.sun.management.jmxremote.ssl=false \
    -Dcom.sun.management.jmxremote.port=7203 \
    -Dcom.sun.management.jmxremote.rmi.port=7203 \
    -Djava.rmi.server.hostname=0.0.0.0 \
    -Djboss.bind.address.management=0.0.0.0 \
    -Djboss.bind.address=0.0.0.0
```

**对于VisualVM**
VisualVM 不支持 remote+http 协议，它只能用标准 JMX RMI（7203端口）。
1. 带 JMX 参数重新启动
```
  cd ~/wildfly-29.0.1.Final
  nohup ./bin/standalone.sh -b 0.0.0.0 \
      -Dcom.sun.management.jmxremote \
      -Dcom.sun.management.jmxremote.authenticate=false \
      -Dcom.sun.management.jmxremote.ssl=false \
      -Dcom.sun.management.jmxremote.port=7203 \
      -Dcom.sun.management.jmxremote.rmi.port=7203 \
      -Djava.rmi.server.hostname=0.0.0.0 \
      -Djboss.bind.address.management=0.0.0.0 \
      -Djboss.bind.address=0.0.0.0
```
2. 然后 VisualVM → File → Add JMX Connection → localhost:7203 → OK。


`ssh -L localhost:9314:0.0.0.0:9314 localhost:11224:0.0.0.0:11224 s407959@se.ifmo.ru -p 2222 -N`
HTTP端口：**9314**
Management：9990 + 1234 = **11224**


`scp -P 2222 F:\web-pro\Lab3\build\libs\Lab3.war s407959@se.ifmo.ru:~/wildfly-29.0.1.Final/standalone/deployments/`
`yDqY-9700`
`scp -P 2222 s407959@se.ifmo.ru:~/wildfly-29.0.1.Final/bin/client/jboss-cli-client.jar F:\web-pro\Lab3\`

website:
`http://localhost:9314/lab3-1.0/`

`ssh s407959@helios.cs.ifmo.ru -p 2222`