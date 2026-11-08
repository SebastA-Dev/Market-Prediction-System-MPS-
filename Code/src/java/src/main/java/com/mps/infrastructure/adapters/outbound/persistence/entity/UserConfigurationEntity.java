package com.mps.infrastructure.adapters.outbound.persistence.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.time.Instant;
import java.util.UUID;

/**
 * Entidad JPA de la tabla 'user_configuration': activos que sigue cada usuario.
 * Nombres de tabla y columnas idénticos a Docs/Scripts.sql.
 */
@Entity
@Table(name = "user_configuration")
public class UserConfigurationEntity {

    @Id
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "target_ticker", nullable = false)
    private AssetEntity asset;

    @Column(name = "alerts_enabled", nullable = false)
    private boolean alertsEnabled;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public UserConfigurationEntity() {
    }

    public UserConfigurationEntity(UUID id, UUID userId, AssetEntity asset, boolean alertsEnabled, Instant createdAt) {
        this.id = id;
        this.userId = userId;
        this.asset = asset;
        this.alertsEnabled = alertsEnabled;
        this.createdAt = createdAt;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    public UUID getUserId() { return userId; }
    public void setUserId(UUID userId) { this.userId = userId; }
    public AssetEntity getAsset() { return asset; }
    public void setAsset(AssetEntity asset) { this.asset = asset; }
    public boolean isAlertsEnabled() { return alertsEnabled; }
    public void setAlertsEnabled(boolean alertsEnabled) { this.alertsEnabled = alertsEnabled; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
