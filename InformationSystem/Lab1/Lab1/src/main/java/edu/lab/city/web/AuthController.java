package edu.lab.city.web;

import edu.lab.city.service.AccountService;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class AuthController {
    private final AccountService accounts;

    public AuthController(AccountService accounts) {
        this.accounts = accounts;
    }

    @GetMapping("/login")
    public String login() {
        return "forward:/auth.html";
    }

    @GetMapping("/auth/csrf")
    @ResponseBody
    public Map<String, String> csrf(CsrfToken token) {
        return Map.of("token", token.getToken(), "header", token.getHeaderName());
    }

    public record Registration(
        @NotBlank(message = "Введите логин.")
        @Pattern(regexp = "[A-Za-z0-9_]{3,32}", message = "Логин: 3–32 латинские буквы, цифры или _.")
        String username,
        @NotNull @Size(min = 8, max = 72, message = "Пароль: от 8 до 72 символов.")
        String password,
        @NotNull String confirmation) {}

    @PostMapping("/auth/register")
    @ResponseBody
    public Map<String, String> register(@Valid @RequestBody Registration input) {
        accounts.register(input.username(), input.password(), input.confirmation());
        return Map.of("message", "Аккаунт создан. Теперь войдите с вашим паролем.");
    }
}
