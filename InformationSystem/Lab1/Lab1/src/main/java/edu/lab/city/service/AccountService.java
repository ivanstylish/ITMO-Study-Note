package edu.lab.city.service;

import edu.lab.city.domain.AppUser;
import edu.lab.city.repository.UserRepository;

import org.springframework.http.HttpStatus;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.nio.charset.StandardCharsets;
import java.util.Locale;

@Service
public class AccountService implements UserDetailsService {
    private final UserRepository users;
    private final PasswordEncoder encoder;

    public AccountService(UserRepository users, PasswordEncoder encoder) {
        this.users = users;
        this.encoder = encoder;
    }

    private String normalize(String name) {
        return name.strip().toLowerCase(Locale.ROOT);
    }

    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String username) {
        var account = users.findByUsername(normalize(username))
            .orElseThrow(() -> new UsernameNotFoundException("Неверный логин или пароль."));
        return User.withUsername(account.getUsername())
            .password(account.getPasswordHash())
            .roles("USER")
            .build();
    }

    @Transactional
    public void register(String username, String password, String confirmation) {
        if (!password.equals(confirmation))
            throw new IllegalArgumentException("Пароли не совпадают.");
        if (password.getBytes(StandardCharsets.UTF_8).length > 72)
            throw new IllegalArgumentException("Пароль слишком длинный: максимум 72 байта UTF-8.");
        String normalized = normalize(username);
        if (users.findByUsername(normalized).isPresent())
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Этот логин уже занят.");
        var account = new AppUser();
        account.setUsername(normalized);
        account.setPasswordHash(encoder.encode(password));
        users.insert(account);
    }
}
