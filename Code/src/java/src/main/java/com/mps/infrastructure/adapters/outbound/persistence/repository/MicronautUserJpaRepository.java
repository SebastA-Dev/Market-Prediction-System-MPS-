package com.mps.infrastructure.adapters.outbound.persistence.repository;

import com.mps.infrastructure.adapters.outbound.persistence.entity.UserEntity;
import io.micronaut.data.annotation.Repository;
import io.micronaut.data.repository.CrudRepository;

import java.util.Optional;
import java.util.UUID;

/**
 * Repositorio Micronaut Data para la entidad UserEntity.
 * Genera consultas SQL en tiempo de compilación para PostgreSQL.
 */
@Repository
public interface MicronautUserJpaRepository extends CrudRepository<UserEntity, UUID> {

    Optional<UserEntity> findByEmail(String email);

    boolean existsByEmail(String email);
}
