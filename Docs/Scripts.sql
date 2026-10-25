-- =============================================================================
-- MPS (Market Prediction System) - Scripts de Creación de Base de Datos SQL
-- Motor: PostgreSQL
-- Fuente: Docs/Requerimentos/MER/UMLBaseDeDatos.drawio (Diagrama UML)
-- Módulo: RDBMS — Gestión de Usuarios, Preferencias y Alertas
-- =============================================================================

-- Habilitar extensiones para soporte de UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. Tabla: "user"
-- Descripción: Almacena los usuarios registrados en la plataforma.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE "user" IS 'Entidad de usuarios del sistema MPS';
COMMENT ON COLUMN "user".id IS 'Identificador único del usuario (UUID)';
COMMENT ON COLUMN "user".email IS 'Correo electrónico único del usuario';
COMMENT ON COLUMN "user".password_hash IS 'Hash de contraseña para autenticación';
COMMENT ON COLUMN "user".created_at IS 'Fecha y hora de registro del usuario';

-- Vista sinónima opcional para compatibilidad con consultas que usen "users"
CREATE OR REPLACE VIEW users AS SELECT * FROM "user";

-- -----------------------------------------------------------------------------
-- 2. Tabla: asset
-- Descripción: Catálogo de activos financieros disponibles para análisis y alertas.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS asset (
    ticker VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE asset IS 'Catálogo de activos financieros monitoreados';
COMMENT ON COLUMN asset.ticker IS 'Símbolo bursátil del activo (PK)';
COMMENT ON COLUMN asset.name IS 'Nombre representativo del activo';
COMMENT ON COLUMN asset.sector IS 'Sector económico al que pertenece el activo';
COMMENT ON COLUMN asset.is_active IS 'Estado del activo en el sistema';

-- -----------------------------------------------------------------------------
-- 3. Tabla: user_configuration
-- Descripción: Preferencias y configuración de monitoreo de alertas por usuario.
-- Relaciones:
--   - user (1:N) define -> user_configuration
--   - asset (1:N) monitorea -> user_configuration
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_configuration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    target_ticker VARCHAR(20) NOT NULL,
    alerts_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_config_user
        FOREIGN KEY (user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_user_config_asset
        FOREIGN KEY (target_ticker)
        REFERENCES asset(ticker)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

COMMENT ON TABLE user_configuration IS 'Configuración de alertas y activos seguidos por usuario';
COMMENT ON COLUMN user_configuration.id IS 'Identificador único de la configuración';
COMMENT ON COLUMN user_configuration.user_id IS 'FK del usuario que define la configuración';
COMMENT ON COLUMN user_configuration.target_ticker IS 'FK del activo que se monitorea';
COMMENT ON COLUMN user_configuration.alerts_enabled IS 'Indica si las alertas están habilitadas';
COMMENT ON COLUMN user_configuration.created_at IS 'Fecha y hora de creación de la regla';

-- -----------------------------------------------------------------------------
-- 4. Tabla: alert_history
-- Descripción: Historial de alertas emitidas y persistidas.
-- Relaciones:
--   - user (1:N) recibe -> alert_history
--   - asset (1:N) origina -> alert_history
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alert_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    price DECIMAL(18, 4) NOT NULL,
    signal VARCHAR(10) NOT NULL,
    triggered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alert_history_user
        FOREIGN KEY (user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_alert_history_asset
        FOREIGN KEY (ticker)
        REFERENCES asset(ticker)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

COMMENT ON TABLE alert_history IS 'Registro histórico de alertas disparadas para usuarios';
COMMENT ON COLUMN alert_history.id IS 'Identificador único del registro de alerta';
COMMENT ON COLUMN alert_history.user_id IS 'FK del usuario que recibe la alerta';
COMMENT ON COLUMN alert_history.ticker IS 'FK del activo financiero que originó la alerta';
COMMENT ON COLUMN alert_history.price IS 'Precio del activo al momento del disparo';
COMMENT ON COLUMN alert_history.signal IS 'Señal cuantitativa (BUY, SELL, HOLD)';
COMMENT ON COLUMN alert_history.triggered_at IS 'Marca temporal en que se disparó la alerta';

-- -----------------------------------------------------------------------------
-- Índices para optimizar las claves foráneas y consultas de historial
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_user_configuration_user_id ON user_configuration(user_id);
CREATE INDEX IF NOT EXISTS idx_user_configuration_target_ticker ON user_configuration(target_ticker);
CREATE INDEX IF NOT EXISTS idx_alert_history_user_id ON alert_history(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_ticker ON alert_history(ticker);
CREATE INDEX IF NOT EXISTS idx_alert_history_triggered_at ON alert_history(triggered_at DESC);
