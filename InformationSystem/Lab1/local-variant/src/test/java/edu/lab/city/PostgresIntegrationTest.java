package edu.lab.city;

import static org.assertj.core.api.Assertions.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.fasterxml.jackson.databind.*;

import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.*;
import org.springframework.test.web.servlet.*;

import java.util.*;

// @SpringBootTest：启动 Spring Boot 测试上下文，连接专门的测试数据库。
@SpringBootTest
// @AutoConfigureMockMvc：自动配置 MockMvc，通过模拟 HTTP 请求验证控制器与安全过滤器。
@AutoConfigureMockMvc
class PostgresIntegrationTest {
    // @Autowired：从测试容器注入所需组件，无需手动创建。
    @Autowired
    MockMvc mvc;
    @Autowired
    ObjectMapper json;
    @Autowired
    JdbcTemplate jdbc;

    // @DynamicPropertySource：为测试动态提供连接配置，确保使用 TEST_DB_URL 指定的独立数据库。
    @DynamicPropertySource
    static void database(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", () -> Objects.requireNonNull(System.getenv("TEST_DB_URL")));
        r.add(
            "spring.datasource.username", () -> System.getenv().getOrDefault("TEST_DB_USER", "lab_test"));
        r.add(
            "spring.datasource.password", () -> System.getenv().getOrDefault("TEST_DB_PASSWORD", ""));
    }

    // @BeforeEach：每个测试开始前执行准备工作；这里会清理测试表。
    @BeforeEach
    void clear() {
        // integrationTest requires explicit TEST_DB_URL; never point it to a working database.
        jdbc.execute(
            "TRUNCATE lab1_info.city, lab1_info.human, lab1_info.coordinates,"
            + " lab1_info.app_user RESTART IDENTITY");
    }

    JsonNode read(MvcResult result) throws Exception {
        return json.readTree(result.getResponse().getContentAsString());
    }

    JsonNode create(String type, Object body) throws Exception {
        return read(mvc.perform(post("/api/" + type)
                .with(user("student"))
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsString(body)))
            .andExpect(status().isOk())
            .andReturn());
    }

    Map<String, Object> city(String name, String point, double area, Long height, String date) {
        Map<String, Object> c = new LinkedHashMap<>();
        c.put("name", name);
        c.put("coordinatesId", point);
        c.put("area", area);
        c.put("population", "9007199254740993");
        c.put("capital", false);
        c.put("metersAboveSeaLevel", height);
        c.put("standardOfLiving", "LOW");
        c.put("establishmentDate", date);
        return c;
    }

    JsonNode point(long x, double y) throws Exception {
        return create("coordinates", Map.of("x", Long.toString(x), "y", y));
    }

    JsonNode operation(String name) throws Exception {
        return read(mvc.perform(get("/api/operations/" + name).with(user("student")))
            .andExpect(status().isOk())
            .andReturn())
            .get("value");
    }

    // @Test：标记一个由 JUnit 执行的测试方法。
    @Test
    void registrationPersistsHashAndAllowsOnlyRegisteredLogins() throws Exception {
        mvc.perform(post("/login")
            .with(csrf())
            .param("username", "new_member")
            .param("password", "Password123"))
            .andExpect(status().isUnauthorized());
        var registration = Map.of(
            "username", "New_Member",
            "password", "Password123",
            "confirmation", "Password123");
        mvc.perform(post("/auth/register")
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content(json.writeValueAsString(registration)))
            .andExpect(status().isOk());
        String hash = jdbc.queryForObject("select password_hash from lab1_info.app_user where username='new_member'",
            String.class);
        assertThat(hash).startsWith("$2a$").isNotEqualTo("Password123");
        var loggedIn = mvc.perform(post("/login")
            .with(csrf())
            .param("username", "NEW_MEMBER")
            .param("password", "Password123"))
            .andExpect(status().isOk())
            .andReturn();
        mvc.perform(get("/api/cities")
            .session((org.springframework.mock.web.MockHttpSession) loggedIn.getRequest().getSession(false)))
            .andExpect(status().isOk());
        mvc.perform(post("/login")
            .with(csrf())
            .param("username", "new_member")
            .param("password", "wrong"))
            .andExpect(status().isUnauthorized());
        mvc.perform(post("/auth/register")
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content(json.writeValueAsString(registration)))
            .andExpect(status().isConflict());
    }

    @Test
    void registrationRequiresCsrfValidFieldsAndMatchingPasswords() throws Exception {
        String valid = json.writeValueAsString(Map.of(
                "username", "valid_user",
                "password", "Password123",
                "confirmation", "Password123"));
        mvc.perform(post("/auth/register").contentType(MediaType.APPLICATION_JSON).content(valid))
            .andExpect(status().isForbidden());
        mvc.perform(post("/auth/register")
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content(json.writeValueAsString(Map.of(
                "username", "x",
                "password", "short",
                "confirmation", "short"))))
            .andExpect(status().isBadRequest());
        mvc.perform(post("/auth/register")
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content(json.writeValueAsString(Map.of(
                "username", "valid_user",
                "password", "Password123",
                "confirmation", "Different"))))
            .andExpect(status().isBadRequest());
        assertThat(jdbc.queryForObject("select count(*) from lab1_info.app_user", Long.class))
            .isZero();
    }

    @Test
    void loginAssetsArePublicAndContainNoDemoAccountRequirement() throws Exception {
        mvc.perform(get("/login")).andExpect(status().isOk()).andExpect(forwardedUrl("/auth.html"));
        mvc.perform(get("/auth.html")).andExpect(status().isOk());
        mvc.perform(get("/auth/csrf"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.token").isNotEmpty());
        mvc.perform(get("/images/cities/shanghai.jpg")).andExpect(status().isOk());
    }

    @Test
    void usesEclipseLinkAndRejectsAnonymousAndMissingCsrf() throws Exception {
        assertThat(jdbc.queryForObject("select count(*) from lab1_info.city", Long.class)).isZero();
        mvc.perform(get("/api/cities")).andExpect(status().isUnauthorized());
        mvc.perform(post("/api/coordinates")
            .with(user("student"))
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"x\":0,\"y\":0}"))
            .andExpect(status().isForbidden());
    }

    @Test
    void crudRelationsRevisionAndConflict() throws Exception {
        String before = read(mvc.perform(get("/api/revision").with(user("student2"))).andReturn())
            .get("revision")
            .asText();
        var p = point(3, 4);
        var h = create(
            "humans", Map.of(
                "name", "Ivan",
                "age", 42,
                "height", 180,
                "birthday", "1990-01-02T03:04:05+03:00[Europe/Moscow]"));
        var input = city("Alpha", p.get("id").asText(), 100, 12L, "2000-01-01T00:00:00");
        input.put("governorId", h.get("id").asText());
        var c = create("cities", input);
        String id = c.get("id").asText();
        assertThat(c.get("population").asText()).isEqualTo("9007199254740993");
        assertThat(c.get("creationDate").asText())
            .isEqualTo(java.time.LocalDate.now(java.time.ZoneOffset.UTC).toString());
        var seen = read(mvc.perform(get("/api/cities/" + id).with(user("student2")))
            .andExpect(status().isOk())
            .andReturn());
        assertThat(seen.at("/governor/name").asText()).isEqualTo("Ivan");
        assertThat(seen.at("/coordinates/x").asText()).isEqualTo("3");
        String after = read(mvc.perform(get("/api/revision").with(user("student2"))).andReturn())
            .get("revision")
            .asText();
        assertThat(after).isNotEqualTo(before);
        mvc.perform(delete("/api/coordinates/" + p.get("id").asText())
            .param("version", p.get("version").asText())
            .with(user("student"))
            .with(csrf()))
            .andExpect(status().isConflict());
        mvc.perform(delete("/api/humans/" + h.get("id").asText())
            .param("version", h.get("version").asText())
            .with(user("student"))
            .with(csrf()))
            .andExpect(status().isConflict());
        input.put("name", "Beta");
        input.put("version", c.get("version").asText());
        mvc.perform(put("/api/cities/" + id)
            .with(user("student"))
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content(json.writeValueAsString(input)))
            .andExpect(status().isOk());
        mvc.perform(put("/api/cities/" + id)
            .with(user("student2"))
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content(json.writeValueAsString(input)))
            .andExpect(status().isConflict());
        var latest = read(mvc.perform(get("/api/cities/" + id).with(user("student2"))).andReturn());
        mvc.perform(delete("/api/cities/" + id)
            .param("version", latest.get("version").asText())
            .with(user("student"))
            .with(csrf()))
            .andExpect(status().isOk());
        mvc.perform(get("/api/cities/" + id).with(user("student2")))
            .andExpect(status().isNotFound());
        mvc.perform(delete("/api/coordinates/" + p.get("id").asText())
            .param("version", p.get("version").asText())
            .with(user("student"))
            .with(csrf()))
            .andExpect(status().isOk());
    }

    @Test
    void allFiveFunctionsAndExactFilter() throws Exception {
        var origin = point(0, 0);
        var end = point(3, 4);
        create("cities", city("Alpha", origin.get("id").asText(), 1, 0L, "1900-01-01T00:00:00"));
        create("cities", city("Alphabet", end.get("id").asText(), 2, 12L, "2000-01-01T00:00:00"));
        create("cities", city("100%_town", origin.get("id").asText(), 2, null, null));
        assertThat(operation("average").asDouble()).isEqualTo(6);
        assertThat(operation("groups").size()).isEqualTo(2);
        assertThat(operation("extremes").asDouble()).isEqualTo(13);
        assertThat(operation("newest").asDouble()).isEqualTo(13);
        var search = read(mvc.perform(get("/api/operations/substring")
                .param("needle", "%_")
                .with(user("student")))
            .andExpect(status().isOk())
            .andReturn());
        assertThat(search.get("value").size()).isEqualTo(1);
        var exact = read(mvc.perform(get("/api/cities")
                .param("column", "name")
                .param("value", "Alpha")
                .with(user("student")))
            .andExpect(status().isOk())
            .andReturn());
        assertThat(exact.get("total").asLong()).isEqualTo(1);
        var page = read(mvc.perform(get("/api/cities")
                .param("page", "1")
                .param("size", "1")
                .param("sort", "name")
                .with(user("student")))
            .andReturn());
        assertThat(page.get("items").size()).isEqualTo(1);
        assertThat(page.at("/items/0/name").asText()).isEqualTo("Alpha");
        mvc.perform(get("/api/cities").param("sort", "name; DROP TABLE city").with(user("student")))
            .andExpect(status().isBadRequest());
    }

    @Test
    void nullsMissingElevationAndSameCity() throws Exception {
        assertThat(operation("average").isNull()).isTrue();
        assertThat(operation("extremes").isNull()).isTrue();
        assertThat(operation("newest").isNull()).isTrue();
        assertThat(operation("groups").size()).isZero();
        var p = point(0, 0);
        create("cities", city("Unknown", p.get("id").asText(), 1, null, "2000-01-01T00:00:00"));
        assertThat(operation("extremes").asDouble()).isZero();
        mvc.perform(get("/api/operations/newest").with(user("student")))
            .andExpect(status().isUnprocessableEntity());
        create("cities", city("Known", p.get("id").asText(), 2, 0L, null));
        mvc.perform(get("/api/operations/extremes").with(user("student")))
            .andExpect(status().isUnprocessableEntity());
    }

    @Test
    void validatesBothHttpAndDirectDatabaseWrites() throws Exception {
        mvc.perform(post("/api/coordinates")
            .with(user("student"))
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"x\":1,\"y\":-531}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.fields.y").exists());
        assertThatThrownBy(() -> jdbc.update("insert into lab1_info.coordinates(x,y) values(1,-531)"))
            .isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class);
        assertThatThrownBy(() -> jdbc.update("insert into lab1_info.coordinates(x,y) values(1,'NaN')"))
            .isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class);
        assertThatThrownBy(() -> jdbc.update(
                "insert into lab1_info.human(name,age,height)"
                + " values('Ivan',0,180)"))
            .isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class);
        var p = point(Long.MAX_VALUE, 0);
        assertThat(p.get("x").asText()).isEqualTo(Long.toString(Long.MAX_VALUE));
        var c = create("cities", city("Safe", p.get("id").asText(), 1, 0L, null));
        assertThatThrownBy(() -> jdbc.update(
                "update lab1_info.city set creation_date = '2000-01-01'"
                + " where id = ?",
                c.get("id").asLong()))
            .isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class);
    }
}
