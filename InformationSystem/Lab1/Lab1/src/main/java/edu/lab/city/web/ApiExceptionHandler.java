package edu.lab.city.web;

import jakarta.persistence.*;
import jakarta.validation.ConstraintViolationException;

import org.springframework.dao.*;
import org.springframework.http.*;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.*;

// @RestControllerAdvice：集中处理控制器异常，并将结果作为 JSON 响应返回。
@RestControllerAdvice
public class ApiExceptionHandler {
    // @ExceptionHandler：指定此方法处理的异常类型，用于统一转换 HTTP 状态与错误消息。
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<?> validation(MethodArgumentNotValidException e) {
        Map<String, String> fields = new LinkedHashMap<>();
        for (var field : e.getBindingResult().getFieldErrors()) {
            fields.put(field.getField(), field.getDefaultMessage());
        }
        var body = Map.of("message", "Invalid field values", "fields", fields);
        return ResponseEntity.badRequest().body(body);
    }

    @ExceptionHandler(ResponseStatusException.class)
    ResponseEntity<?> status(ResponseStatusException e) {
        String message = Objects.toString(e.getReason(), "Request failed");
        return ResponseEntity.status(e.getStatusCode()).body(Map.of("message", message));
    }

    @ExceptionHandler({
        IllegalArgumentException.class,
        HttpMessageNotReadableException.class,
        ConstraintViolationException.class
    })
    ResponseEntity<?> badInput(Exception e) {
        String message = Objects.toString(e.getMessage(), "Invalid values");
        if (e instanceof HttpMessageNotReadableException) {
            message = "Invalid JSON, date format, enum, integer range or"
                + " unexpected field. Check all fields.";
        }
        return error(400, message);
    }

    @ExceptionHandler({OptimisticLockException.class, OptimisticLockingFailureException.class})
    ResponseEntity<?> conflict(Exception e) {
        return error(409, "Concurrent update detected. Close this dialog and reload the object.");
    }

    @ExceptionHandler({
        DataAccessException.class,
        PersistenceException.class,
        org.springframework.transaction.TransactionSystemException.class
    })
    ResponseEntity<?> database(Exception e) {
        Throwable t = e;
        while (t != null) {
            if (t instanceof java.sql.SQLException sql) {
                String state = sql.getSQLState();
                // 用户名唯一约束兜底：两个请求同时注册时，也不会创建重复账号。
                if ("23505".equals(state)) {
                    return error(409, "Этот логин уже занят.");
                }
                if ("23503".equals(state)) {
                    String message = "Cannot delete a referenced object, or the selected"
                        + " related object no longer exists. Unlink it from cities first.";
                    return error(409, message);
                }
                if ("22023".equals(state)) {
                    String message = "Route cannot be calculated: a selected city has no metersAboveSeaLevel.";
                    return error(422, message);
                }
                if (state != null && state.startsWith("23")) {
                    String message = "Database constraint rejected the values. Check"
                        + " positive numbers, required fields and relationships.";
                    return error(400, message);
                }
                if ("22003".equals(state)) {
                    return error(400, "Numbers are too large for this calculation.");
                }
            }
            if (t instanceof ConstraintViolationException c) return badInput(c);
            t = t.getCause();
        }
        return error(500, "Database operation failed. Check the server log and database connection.");
    }

    // 统一组装错误响应，避免每个分支重复嵌套 ResponseEntity、body 和 Map.of。
    private ResponseEntity<?> error(int status, String message) {
        return ResponseEntity.status(status).body(Map.of("message", message));
    }
}
