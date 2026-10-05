package edu.lab.city.web;

import edu.lab.city.service.AccountService;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

// @Controller：声明 MVC 控制器，可以返回页面名或转发路径。
@Controller
public class AuthController {
    private final AccountService accounts;

    public AuthController(AccountService accounts) {
        this.accounts = accounts;
    }

    // @GetMapping：将 HTTP GET 请求映射到此方法，通常用于查询数据或打开页面。
    @GetMapping("/login")
    public String login() {
        return "forward:/auth.html";
    }

    @GetMapping("/auth/csrf")
    // @ResponseBody：将返回值直接写入 HTTP 响应体，而不是作为页面名称。
    @ResponseBody
    public Map<String, String> csrf(CsrfToken token) {
        return Map.of("token", token.getToken(), "header", token.getHeaderName());
    }

    public record Registration(
        // @NotBlank：校验字符串不能为 null、空串或只有空白字符。
        @NotBlank(message = "Введите логин.")
        // @Pattern：使用正则表达式校验字符串格式，例如用户名允许的字符和长度。
        @Pattern(regexp = "[A-Za-z0-9_]{3,32}", message = "Логин: 3–32 латинские буквы, цифры или _.")
        String username,
        // @NotNull：校验值不能为 null；它不负责判断字符串是否为空或数字是否为正。
        // @Size：限制字符串长度或集合大小；非空要求需另用 NotNull 或 NotBlank。
        @NotNull @Size(min = 8, max = 72, message = "Пароль: от 8 до 72 символов.")
        String password,
        @NotNull String confirmation) {}

    // @PostMapping：将 HTTP POST 请求映射到此方法，通常用于创建数据或提交操作。
    @PostMapping("/auth/register")
    @ResponseBody
    // @Valid：触发关联对象或请求 DTO 内部的校验约束，而不是只检查外层引用。
    // @RequestBody：把 HTTP 请求体中的 JSON 解析成参数对象。
    public Map<String, String> register(@Valid @RequestBody Registration input) {
        accounts.register(input.username(), input.password(), input.confirmation());
        return Map.of("message", "Аккаунт создан. Теперь войдите с вашим паролем.");
    }
}
