package edu.lab.city.service;

import edu.lab.city.domain.*;
import edu.lab.city.dto.Requests.*;
import edu.lab.city.repository.ObjectRepository;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.*;

// @Service：声明业务层 Spring Bean，由容器创建并注入其依赖。
@Service
// @Transactional：在事务中执行方法；readOnly=true 标记只读意图，提交与回滚由事务管理器处理。
@Transactional
public class CityService {
    private final ObjectRepository repository;

    public CityService(ObjectRepository repository) {
        this.repository = repository;
    }

    public <T> T get(Class<T> type, long id) {
        T result = repository.find(type, id);
        if (result == null) {
            throw new ResponseStatusException(
                HttpStatus.NOT_FOUND, type.getSimpleName() + " #" + id + " not found"
            );
        }
        return result;
    }

    @Transactional(readOnly = true)
    public Page<City> list(
        int page, int size, String column, String value, String sort, boolean desc) {
        var strings = Set.of("name", "governorName", "climate", "government", "standardOfLiving");
        if ((!sort.equals("id") && !strings.contains(sort))
            || (!column.isEmpty() && !strings.contains(column))) {
            throw new IllegalArgumentException("Unknown string column or sort field");
        }
        if (page < 0 || size < 1 || size > 100 || page > Integer.MAX_VALUE / size) {
            throw new IllegalArgumentException("page must be >= 0; size must be 1..100");
        }
        return repository.cities(page, size, column, value, sort, desc);
    }

    @Transactional(readOnly = true)
    public <T> List<T> all(Class<T> type) {
        return repository.all(type);
    }

    private void version(Long actual, Long expected) {
        // 检查用户打开表单时的版本；过期表单不能覆盖其他用户的新修改。
        if (expected == null || !expected.equals(actual)) {
            String message = "Object was changed by another user. Close this dialog and reload before editing.";
            throw new ResponseStatusException(HttpStatus.CONFLICT, message);
        }
    }

    public City saveCity(Long id, CityInput input) {
        // 同一个方法处理新增与修改；关联对象必须先在数据库中存在。
        if (!Float.isFinite(input.area()))
            throw new IllegalArgumentException("area must be finite");
        City city = id == null ? new City() : get(City.class, id);
        if (id != null) version(city.getVersion(), input.version());
        city.setName(input.name());
        city.setCoordinates(get(Coordinates.class, input.coordinatesId()));
        city.setArea(input.area());
        city.setPopulation(input.population());
        city.setEstablishmentDate(input.establishmentDate());
        city.setCapital(input.capital());
        city.setMetersAboveSeaLevel(input.metersAboveSeaLevel());
        city.setClimate(input.climate());
        city.setGovernment(input.government());
        city.setStandardOfLiving(input.standardOfLiving());
        city.setGovernor(input.governorId() == null ? null : get(Human.class, input.governorId()));
        if (id == null) return repository.insert(city);
        repository.flush();
        return city;
    }

    public Coordinates saveCoordinates(Long id, CoordinatesInput input) {
        if (!Double.isFinite(input.y())) throw new IllegalArgumentException("y must be finite");
        Coordinates point = id == null ? new Coordinates() : get(Coordinates.class, id);
        if (id != null) version(point.getVersion(), input.version());
        point.setX(input.x());
        point.setY(input.y());
        if (id == null) return repository.insert(point);
        repository.flush();
        return point;
    }

    public Human saveHuman(Long id, HumanInput input) {
        if (!Float.isFinite(input.height()))
            throw new IllegalArgumentException("height must be finite");
        Human person = id == null ? new Human() : get(Human.class, id);
        if (id != null) version(person.getVersion(), input.version());
        person.setName(input.name());
        person.setAge(input.age());
        person.setHeight(input.height());
        person.setBirthday(input.birthday());
        if (id == null) return repository.insert(person);
        repository.flush();
        return person;
    }

    public <T> void delete(Class<T> type, long id, long expectedVersion) {
        T object = get(type, id);
        Long actual;
        if (object instanceof City city) {
            actual = city.getVersion();
        } else if (object instanceof Human human) {
            actual = human.getVersion();
        } else {
            actual = ((Coordinates) object).getVersion();
        }
        version(actual, expectedVersion);
        // 不使用级联删除。数据库外键会原子地阻止删除仍被城市引用的坐标或人物。
        repository.remove(object);
    }
}
