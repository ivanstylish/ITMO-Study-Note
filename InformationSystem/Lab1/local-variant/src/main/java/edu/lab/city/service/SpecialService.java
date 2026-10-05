package edu.lab.city.service;

import edu.lab.city.dto.Requests.Result;
import edu.lab.city.repository.SpecialRepository;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

// @Service：声明业务层 Spring Bean，由容器创建并注入其依赖。
@Service
// @Transactional：在事务中执行方法；readOnly=true 标记只读意图，提交与回滚由事务管理器处理。
@Transactional(readOnly = true)
public class SpecialService {
    private final SpecialRepository repository;

    public SpecialService(SpecialRepository repository) {
        this.repository = repository;
    }

    public String revision() {
        return repository.revision();
    }

    public Result run(String operation, String needle) {
        return switch (operation) {
            case "average" -> new Result(
                repository.average(),
                "NULL elevations are excluded; null result means no known elevations."
            );
            case "groups" -> {
                var groups = repository.groups().stream()
                    .map(row -> Map.of("area", row[0], "count", row[1]))
                    .toList();
                yield new Result(groups, "Groups use the stored PostgreSQL real value.");
            }
            case "substring" -> new Result(
                repository.containing(needle),
                "Literal, case-sensitive substring; an empty substring matches all names."
            );
            case "extremes" -> new Result(
                repository.extremeRoute(),
                "3D Euclidean distance. Ties: smallest ID. Empty table: null. Same city: 0."
                    + " Missing endpoint elevation: error."
            );
            case "newest" -> new Result(
                repository.newestRoute(),
                "Distance from (0,0,0) to the latest establishmentDate; unknown dates excluded."
                    + " Ties: smallest ID. No eligible city: null. Missing elevation: error."
            );
            default -> throw new IllegalArgumentException("Unknown operation");
        };
    }
}
