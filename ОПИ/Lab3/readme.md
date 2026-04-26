# Лабораторная работа №3 — Apache Ant Build Script
## Проект: CoordinateCheck (Jakarta EE + JSF + JPA)

---

## Структура проекта (ожидаемая для Ant)

```
project-root/
├── build.xml                    ← Главный Ant-скрипт
├── build.properties             ← Все переменные и константы
├── history.sh                   ← Shell-скрипт для цели history (Linux/macOS)
│
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── org/coordinate/
│   │   │       ├── bean/
│   │   │       │   ├── ClockBean.java
│   │   │       │   ├── PointBean.java
│   │   │       │   ├── ResultBean.java
│   │   │       │   └── ResultDTO.java
│   │   │       ├── entity/
│   │   │       │   └── Result.java
│   │   │       └── service/
│   │   │           └── AreaCheck.java
│   │   ├── resources/
│   │   │   └── META-INF/
│   │   │       └── persistence.xml
│   │   └── webapp/
│   │       ├── WEB-INF/
│   │       │   ├── beans.xml
│   │       │   ├── faces-config.xml
│   │       │   └── web.xml
│   │       ├── resources/
│   │       │   ├── css/style.css
│   │       │   └── js/main.js
│   │       ├── index.xhtml
│   │       └── main.xhtml
│   └── test/
│       └── java/
│           └── org/coordinate/service/
│               └── AreaCheckTest.java   ← JUnit 5 тесты
│
├── lib/
│   ├── compile/                 ← Jakarta EE API jars (provided scope)
│   │   ├── jakarta.jakartaee-api-10.0.0.jar
│   │   └── ... (другие нужные jars)
│   └── test/
│       ├── junit-platform-console-standalone-1.10.0.jar
│       └── ... (другие test jars)
│
├── resources/
│   └── build-complete.wav       ← Звуковой файл для цели music
│
└── build/                       ← Создаётся автоматически
    ├── classes/                 ← Скомпилированные .class файлы
    ├── dist/                    ← JAR-архив
    └── test/
        ├── classes/             ← Скомпилированные тесты
        └── reports/             ← JUnit XML и HTML отчёты
```

---

## Использование

### Предварительные требования

1. **Apache Ant** ≥ 1.10 установлен и доступен как `ant` в PATH
2. **JDK 17+** установлен
3. Папка `lib/compile/` содержит Jakarta EE API jars
4. Папка `lib/test/` содержит JUnit 5 standalone jar

### Установка Apache Ant (Ubuntu/Debian)
```bash
sudo apt install ant
# или вручную: https://ant.apache.org/bindownload.cgi
```

### Цели (targets)

| Команда           | Описание                                              |
|-------------------|-------------------------------------------------------|
| `ant compile`     | Компиляция исходников в `build/classes/`              |
| `ant build`       | Компиляция + упаковка в `build/dist/CoordinateCheck-1.0.0.jar` |
| `ant clean`       | Удаление `build/` и временных файлов                 |
| `ant test`        | Запуск JUnit тестов (сначала вызывает `build`)        |
| `ant music`       | Воспроизведение музыки (вызывается автоматически из `build`) |
| `ant history`     | Откат по git при ошибке компиляции + генерация diff  |

### Примеры

```bash
# Собрать проект
ant build

# Запустить тесты
ant test

# Очистить и пересобрать
ant clean build

# Поиск последней рабочей ревизии при ошибке компиляции
ant history
```

---

## Что делает MANIFEST.MF

Файл создаётся автоматически при `ant build`:

```
Manifest-Version: 1.0
Implementation-Title: CoordinateCheck
Implementation-Version: 1.0.0
Implementation-Vendor: ITMO University
Main-Class: org.coordinate.bean.PointBean
Built-By: <username>
Build-Jdk: 17.x.x
```

---

## Цель history — подробнее

Алгоритм работы `history.sh`:

```
1. ant history вызывается пользователем
2. Ant пробует скомпилировать текущий код (compile-silent)
3. Если компиляция OK → вывод "Откат не нужен"
4. Если ошибка → запускается history.sh
   ┌─────────────────────────────────────────┐
   │  Получаем список всех git-коммитов      │
   │  Начиная с предпоследнего:              │
   │    git checkout <rev>                   │
   │    javac ... (тихая компиляция)         │
   │    Если OK → LAST_WORKING = rev, break  │
   │    Если нет → следующая ревизия         │
   └─────────────────────────────────────────┘
5. Если LAST_WORKING найден:
   - Определяем NEXT_REV (следующая за LAST_WORKING = сломавшая сборку)
   - git diff LAST_WORKING NEXT_REV > broken_diff_TIMESTAMP.diff
6. git checkout <исходная ветка>
7. Вывод отчёта
```

---

## Цель music — подробнее

- Автоматически определяет ОС (Linux/macOS/Windows)
- Linux: использует `aplay` (для .wav файлов)
- macOS: использует `afplay`  
- Windows: использует `wmplayer`
- Файл указывается в `build.properties`: `music.file=resources/build-complete.wav`
- Выполняется **после успешной сборки** (`build` вызывает `antcall target="music"`)

---

## Зависимости для компиляции

Для Jakarta EE проекта нужны следующие jar в `lib/compile/`:

```bash
# Скачать Jakarta EE API (WildFly/GlassFish provided)
# Например, с Maven Central:
mvn dependency:copy \
  -Dartifact=jakarta.platform:jakarta.jakartaee-api:10.0.0:jar \
  -DoutputDirectory=lib/compile/
```

Для тестов в `lib/test/`:
```bash
# JUnit 5 standalone (включает всё необходимое)
# https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/
wget -P lib/test/ \
  https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.10.0/junit-platform-console-standalone-1.10.0.jar
```