package com.example.backend.controller;

import com.example.backend.dto.LoginDto;
import com.example.backend.service.UserService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final AuthenticationManager authenticationManager;
    private final UserService userService;

    public AuthController(AuthenticationManager authenticationManager, UserService userService) {
        this.authenticationManager = authenticationManager;
        this.userService = userService;
    }

    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody LoginDto dto) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(dto.getUsername(), dto.getPassword()));
            SecurityContextHolder.getContext().setAuthentication(authentication);
            return ResponseEntity.ok("Logged in");
        } catch (Exception e) {
            return ResponseEntity.status(401).body("Invalid username or password");
        }
    }

    @PostMapping("/register")
    public ResponseEntity<String> register(@RequestBody LoginDto dto) {
        if (userService.existsByUsername(dto.getUsername())) {
            return ResponseEntity.badRequest().body("Username is already taken.");
        }
        return ResponseEntity.ok("Registration successful. Please log in.");
    }

    @PostMapping("/logout")
    public ResponseEntity<String> logout() {
        SecurityContextHolder.clearContext();
        return ResponseEntity.ok("Logged out");
    }
}