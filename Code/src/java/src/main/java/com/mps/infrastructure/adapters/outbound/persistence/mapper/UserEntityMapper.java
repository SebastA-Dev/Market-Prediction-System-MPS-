package com.mps.infrastructure.adapters.outbound.persistence.mapper;

import com.mps.domain.model.User;
import com.mps.infrastructure.adapters.outbound.persistence.entity.UserEntity;
import jakarta.inject.Singleton;

/**
 * Mapeador bidireccional entre la entidad de dominio User y la entidad JPA UserEntity.
 */
@Singleton
public class UserEntityMapper {

    public UserEntity toEntity(User domain) {
        if (domain == null) return null;
        return new UserEntity(
                domain.getId(),
                domain.getEmail(),
                domain.getPasswordHash(),
                domain.getCreatedAt()
        );
    }

    public User toDomain(UserEntity entity) {
        if (entity == null) return null;
        return new User(
                entity.getId(),
                entity.getEmail(),
                entity.getPasswordHash(),
                entity.getCreatedAt()
        );
    }
}
