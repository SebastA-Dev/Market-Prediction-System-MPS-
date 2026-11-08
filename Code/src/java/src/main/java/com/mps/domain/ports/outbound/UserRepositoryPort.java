package com.mps.domain.ports.outbound;

import com.mps.domain.model.User;

import java.util.Optional;
import java.util.UUID;

/**
 * Puerto secundario (Driven / Outbound Port) para la persistencia de usuarios.
 * Agnóstico de la base de datos relacional (PostgreSQL).
 */
public interface UserRepositoryPort {

    User save(User user);

    Optional<User> findById(UUID id);

    Optional<User> findByEmail(String email);

    boolean existsByEmail(String email);
}
