package com.mps.domain.model;

import com.mps.domain.exception.InvalidUserDataException;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * Entidad de dominio pura de Usuario bajo Arquitectura Hexagonal (RNF-13).
 * Completamente agnóstica de frameworks e infraestructura (sin anotaciones de JPA, Micronaut ni Jackson).
 */
public class User {

    private static final Pattern EMAIL_PATTERN = Pattern.compile(
            "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
    );

    private final UUID id;
    private final String email;
    private final String passwordHash;
    private final Instant createdAt;

    public User(UUID id, String email, String passwordHash, Instant createdAt) {
        this.id = Objects.requireNonNull(id, "User ID cannot be null");
        this.email = validateEmail(email);
        this.passwordHash = validatePasswordHash(passwordHash);
        this.createdAt = Objects.requireNonNull(createdAt, "CreatedAt cannot be null");
    }

    /**
     * Factory method para crear un nuevo usuario con identificador criptográfico único (UUID v4)
     * y marca temporal actual, conforme a RF-21 y RNF-23.
     */
    public static User create(String email, String passwordHash) {
        return new User(UUID.randomUUID(), email, passwordHash, Instant.now());
    }

    private static String validateEmail(String email) {
        if (email == null || email.trim().isEmpty()) {
            throw new InvalidUserDataException("Email cannot be null or empty");
        }
        String normalized = email.trim().toLowerCase();
        if (!EMAIL_PATTERN.matcher(normalized).matches()) {
            throw new InvalidUserDataException("Invalid email syntax: " + email);
        }
        if (normalized.length() > 255) {
            throw new InvalidUserDataException("Email exceeds maximum length of 255 characters");
        }
        return normalized;
    }

    private static String validatePasswordHash(String passwordHash) {
        if (passwordHash == null || passwordHash.trim().isEmpty()) {
            throw new InvalidUserDataException("Password hash cannot be null or empty");
        }
        return passwordHash.trim();
    }

    public UUID getId() {
        return id;
    }

    public String getEmail() {
        return email;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User other)) return false;
        return Objects.equals(id, other.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", email='" + email + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
