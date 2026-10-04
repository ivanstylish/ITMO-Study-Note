package edu.lab.city.config;

import jakarta.servlet.http.HttpServletResponse;

import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;

import java.io.IOException;

@Configuration
public class SecurityConfig {
    @Bean
    PasswordEncoder encoder() {
        return new BCryptPasswordEncoder();
    }

    private static void json(HttpServletResponse response, int status, String message)
        throws IOException {
        response.setStatus(status);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"message\":\"" + message + "\"}");
    }

    @Bean
    SecurityFilterChain security(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
            .requestMatchers(
                "/login", "/auth.html", "/auth/**", "/auth.css", "/auth.js",
                "/ui.js", "/ui.css", "/i18n.js", "/images/**", "/error"
            ).permitAll()
            .anyRequest().authenticated()
        );

        http.formLogin(form -> form
            .loginPage("/login")
            .loginProcessingUrl("/login")
            .successHandler((req, res, auth) -> json(res, 200, "OK"))
            .failureHandler((req, res, error) -> json(res, 401, "Неверный логин или пароль."))
        );

        String expiredMessage = "Обновите страницу и повторите действие: сеанс проверки устарел.";
        http.exceptionHandling(errors -> errors
            .defaultAuthenticationEntryPointFor(
                (req, res, error) -> json(res, 401, "Сессия завершена. Войдите снова."),
                new AntPathRequestMatcher("/api/**")
            )
            .accessDeniedHandler((req, res, error) -> json(res, 403, expiredMessage))
        );

        http.logout(logout -> logout.logoutSuccessHandler((req, res, auth) -> json(res, 200, "OK")));
        return http.build();
    }
}
