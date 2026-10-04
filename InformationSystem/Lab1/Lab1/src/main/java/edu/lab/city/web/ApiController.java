package edu.lab.city.web;

import edu.lab.city.domain.*;
import edu.lab.city.dto.Requests.*;
import edu.lab.city.service.*;

import jakarta.validation.Valid;

import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;
import java.util.*;

@RestController
@RequestMapping("/api")
public class ApiController {
    private final CityService cities;
    private final SpecialService special;

    public ApiController(CityService cities, SpecialService special) {
        this.cities = cities;
        this.special = special;
    }

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
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "") String column,
        @RequestParam(defaultValue = "") String value,
        @RequestParam(defaultValue = "id") String sort,
        @RequestParam(defaultValue = "false") boolean desc) {
        return cities.list(page, size, column, value, sort, desc);
    }

    @GetMapping("/cities/{id}")
    public City city(@PathVariable long id) {
        return cities.get(City.class, id);
    }

    @PostMapping("/cities")
    public City addCity(@Valid @RequestBody CityInput input) {
        return cities.saveCity(null, input);
    }

    @PutMapping("/cities/{id}")
    public City editCity(@PathVariable long id, @Valid @RequestBody CityInput input) {
        return cities.saveCity(id, input);
    }

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
