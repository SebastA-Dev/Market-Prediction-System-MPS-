package com.mps.infrastructure.adapters.outbound.persistence.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * Entidad JPA de la tabla 'asset' (catálogo de activos financieros).
 * Nombres de tabla y columnas idénticos a Docs/Scripts.sql.
 */
@Entity
@Table(name = "asset")
public class AssetEntity {

    @Id
    @Column(name = "ticker", nullable = false, length = 20)
    private String ticker;

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "sector", nullable = false, length = 50)
    private String sector;

    @Column(name = "is_active", nullable = false)
    private boolean active;

    public AssetEntity() {
    }

    public AssetEntity(String ticker, String name, String sector, boolean active) {
        this.ticker = ticker;
        this.name = name;
        this.sector = sector;
        this.active = active;
    }

    public String getTicker() { return ticker; }
    public void setTicker(String ticker) { this.ticker = ticker; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getSector() { return sector; }
    public void setSector(String sector) { this.sector = sector; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
}
