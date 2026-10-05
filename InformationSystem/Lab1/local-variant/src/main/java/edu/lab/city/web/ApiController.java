package edu.lab.city.web;

import edu.lab.city.domain.*;
import edu.lab.city.dto.Requests.*;
import edu.lab.city.service.*;

import jakarta.validation.Valid;

import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;
import java.util.*;

// @RestController：声明返回响应体的 MVC 控制器；本项目由 Jackson 将结果转换为 JSON。
@RestController
// @RequestMapping：设置此控制器所有接口共用的 URL 前缀。
@RequestMapping("/api")
public class ApiController {
    private final CityService cities;
    private final SpecialService special;

    public ApiController(CityService cities, SpecialService special) {
        this.cities = cities;
        this.special = special;
    }

    // @GetMapping：将 HTTP GET 请求映射到此方法，通常用于查询数据或打开页面。
    @GetMapping("/session")
    public Map<String, String> session(Principal principal, CsrfToken token) {
        return Map.of(
            "username", principal.getName(),
            "token", token.getToken(),
            "header", token.getHeaderName()
        );
    }

    @GetMapping("/revision")
    public Map<String, String> revision() {
        return Map.of("revision", special.revision());
    }

    @GetMapping("/cities")
    public Page<City> list(
        // @RequestParam：从 URL 查询参数读取值；defaultValue 指定未提供参数时的默认值。
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "") String column,
        @RequestParam(defaultValue = "") String value,
        @RequestParam(defaultValue = "id") String sort,
        @RequestParam(defaultValue = "false") boolean desc) {
        return cities.list(page, size, column, value, sort, desc);
    }

    @GetMapping("/cities/{id}")
    // @PathVariable：读取 URL 路径占位符的值，例如 cities/{id} 中的 id。
    public City city(@PathVariable long id) {
        return cities.get(City.class, id);
    }

    // @PostMapping：将 HTTP POST 请求映射到此方法，通常用于创建数据或提交操作。
    @PostMapping("/cities")
    // @Valid：触发关联对象或请求 DTO 内部的校验约束，而不是只检查外层引用。
    // @RequestBody：把 HTTP 请求体中的 JSON 解析成参数对象。
    public City addCity(@Valid @RequestBody CityInput input) {
        return cities.saveCity(null, input);
    }

    // @PutMapping：将 HTTP PUT 请求映射到此方法，用于提交对象修改。
    @PutMapping("/cities/{id}")
    public City editCity(@PathVariable long id, @Valid @RequestBody CityInput input) {
        return cities.saveCity(id, input);
    }

    // @DeleteMapping：将 HTTP DELETE 请求映射到此方法，用于删除指定对象。
    @DeleteMapping("/cities/{id}")
    public void deleteCity(@PathVariable long id, @RequestParam long version) {
        cities.delete(City.class, id, version);
    }

    @GetMapping("/coordinates")
    public List<Coordinates> coordinates() {
        return cities.all(Coordinates.class);
    }

    @GetMapping("/coordinates/{id}")
    public Coordinates coordinates(@PathVariable long id) {
        return cities.get(Coordinates.class, id);
    }

    @PostMapping("/coordinates")
    public Coordinates addCoordinates(@Valid @RequestBody CoordinatesInput input) {
        return cities.saveCoordinates(null, input);
    }

    @PutMapping("/coordinates/{id}")
    public Coordinates editCoordinates(
        @PathVariable long id, @Valid @RequestBody CoordinatesInput input) {
        return cities.saveCoordinates(id, input);
    }

    @DeleteMapping("/coordinates/{id}")
    public void deleteCoordinates(@PathVariable long id, @RequestParam long version) {
        cities.delete(Coordinates.class, id, version);
    }

    @GetMapping("/humans")
    public List<Human> humans() {
        return cities.all(Human.class);
    }

    @GetMapping("/humans/{id}")
    public Human human(@PathVariable long id) {
        return cities.get(Human.class, id);
    }

    @PostMapping("/humans")
    public Human addHuman(@Valid @RequestBody HumanInput input) {
        return cities.saveHuman(null, input);
    }

    @PutMapping("/humans/{id}")
    public Human editHuman(@PathVariable long id, @Valid @RequestBody HumanInput input) {
        return cities.saveHuman(id, input);
    }

    @DeleteMapping("/humans/{id}")
    public void deleteHuman(@PathVariable long id, @RequestParam long version) {
        cities.delete(Human.class, id, version);
    }

    @GetMapping("/operations/{operation}")
    public Result operation(
        @PathVariable String operation, @RequestParam(defaultValue = "") String needle) {
        return special.run(operation, needle);
    }
}
