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

// @Service：声明业务层 Spring Bean，由容器创建并注入其依赖。
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

    // @Override：声明此方法实现或重写父类型方法，让编译器检查方法签名。
    @Override
    // @Transactional：在事务中执行方法；readOnly=true 标记只读意图，提交与回滚由事务管理器处理。
    @Transactional(readOnly = true)
    // Spring Security 登录时从数据库读取账号；不再使用内存中的演示用户。
    public UserDetails loadUserByUsername(String username) {
        var account = users.findByUsername(normalize(username))
            .orElseThrow(() -> new UsernameNotFoundException("Неверный логин или пароль."));
        return User.withUsername(account.getUsername())
            .password(account.getPasswordHash())
            .roles("USER")
            .build();
    }

    @Transactional
    // 注册在一个事务中完成，数据库只保存 BCrypt 哈希，不保存原始密码。
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
