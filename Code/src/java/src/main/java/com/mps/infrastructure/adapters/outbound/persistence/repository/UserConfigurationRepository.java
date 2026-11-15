package com.mps.infrastructure.adapters.outbound.persistence.repository;

import com.mps.infrastructure.adapters.outbound.persistence.entity.UserConfigurationEntity;
import io.micronaut.data.annotation.Join;
import io.micronaut.data.annotation.Repository;
import io.micronaut.data.repository.CrudRepository;
import jakarta.transaction.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * Repositorio Micronaut Data (ORM) para 'user_configuration'.
 * Trae en una sola consulta la configuración del usuario junto con su activo (JOIN a 'asset').
 */
@Repository
public interface UserConfigurationRepository extends CrudRepository<UserConfigurationEntity, UUID> {

    @Join(value = "asset", type = Join.Type.FETCH)
    List<UserConfigurationEntity> findByUserIdOrderByCreatedAtAsc(UUID userId);

    /**
     * Elimina del portafolio del usuario el activo indicado (solo filas de ese usuario).
     *
     * @return número de filas borradas (0 si el usuario no seguía ese activo).
     */
    @Transactional
    long deleteByUserIdAndAssetTicker(UUID userId, String ticker);
}
