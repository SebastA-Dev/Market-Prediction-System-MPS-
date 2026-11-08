package com.mps.infrastructure.adapters.outbound.persistence.adapter;

import com.mps.domain.model.User;
import com.mps.domain.ports.outbound.UserRepositoryPort;
import com.mps.infrastructure.adapters.outbound.persistence.entity.UserEntity;
import com.mps.infrastructure.adapters.outbound.persistence.mapper.UserEntityMapper;
import com.mps.infrastructure.adapters.outbound.persistence.repository.MicronautUserJpaRepository;
import jakarta.inject.Singleton;
import jakarta.transaction.Transactional;

import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Adaptador secundario de persistencia para PostgreSQL.
 * Implementa el puerto UserRepositoryPort aislando la base de datos de la lógica de negocio.
 */
@Singleton
public class PostgresUserRepositoryAdapter implements UserRepositoryPort {

    private final MicronautUserJpaRepository repository;
    private final UserEntityMapper mapper;

    public PostgresUserRepositoryAdapter(MicronautUserJpaRepository repository, UserEntityMapper mapper) {
        this.repository = Objects.requireNonNull(repository, "MicronautUserJpaRepository cannot be null");
        this.mapper = Objects.requireNonNull(mapper, "UserEntityMapper cannot be null");
    }

    @Override
    @Transactional
    public User save(User user) {
        Objects.requireNonNull(user, "User domain entity cannot be null");
        UserEntity entity = mapper.toEntity(user);
        UserEntity savedEntity = repository.save(entity);
        return mapper.toDomain(savedEntity);
    }

    @Override
    public Optional<User> findById(UUID id) {
        if (id == null) return Optional.empty();
        return repository.findById(id).map(mapper::toDomain);
    }

    @Override
    public Optional<User> findByEmail(String email) {
        if (email == null) return Optional.empty();
        return repository.findByEmail(email).map(mapper::toDomain);
    }

    @Override
    public boolean existsByEmail(String email) {
        if (email == null) return false;
        return repository.existsByEmail(email);
    }
}
