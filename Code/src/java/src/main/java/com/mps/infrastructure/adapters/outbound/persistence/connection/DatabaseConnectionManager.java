package com.mps.infrastructure.adapters.outbound.persistence.connection;

import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.SQLException;

import javax.sql.DataSource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import jakarta.inject.Singleton;

/**
 * Gestor de conexiones de base de datos para PostgreSQL.
 * <p>
 * Implementado en la capa de infraestructura conforme a Arquitectura Hexagonal (RNF-13, RF-28).
 * Utiliza el pool de conexiones optimizado HikariCP provisto por la dependencia
 * {@code io.micronaut.sql:micronaut-jdbc-hikari} y el driver {@code org.postgresql:postgresql},
 * configurados en {@code application.yml} mediante snakeyaml (RNF-17: pool máximo de 20 conexiones, timeout de 250 ms).
 * </p>
 */
@Singleton
public record DatabaseConnectionManager(DataSource dataSource) {

    private static final Logger LOG = LoggerFactory.getLogger(DatabaseConnectionManager.class);
    private static final int VALIDATION_TIMEOUT_SECONDS = 2;

    /**
     * Obtiene una conexión activa del pool administrado por HikariCP.
     *
     * @return Conexión SQL abierta.
     * @throws SQLException Si ocurre un error de conectividad o se agota el timeout de adquisición.
     */
    public Connection getConnection() throws SQLException {
        try {
            return dataSource.getConnection();
        } catch (SQLException e) {
            LOG.error("Error al adquirir conexión de base de datos desde el pool HikariCP: {}", e.getMessage(), e);
            throw e;
        }
    }

    /**
     * Valida si el enlace con la base de datos PostgreSQL está operativo usando el DataSource.
     *
     * @return true si la conexión responde dentro del tiempo límite; false en caso contrario.
     */
    public boolean isConnectionHealthy() {
        try (Connection connection = getConnection()) {
            return verifyConnection(connection);
        } catch (SQLException e) {
            LOG.warn("Fallo en la prueba de salud de conexión a base de datos: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Abre y verifica la conexión a la base de datos utilizando los parámetros provistos
     * desde la configuración YAML de Micronaut.
     *
     * @param dbUrl    URL de la base de datos configurada en application.yml.
     * @param user     Usuario de conexión configurado en application.yml.
     * @param poolSize Tamaño máximo del pool HikariCP (RNF-17).
     * @param timeout  Timeout de adquisición en milisegundos (RNF-17).
     * @return Conexión SQL activa y verificada.
     * @throws SQLException Si la conexión no puede abrirse o no responde adecuadamente.
     */
    public Connection openAndVerifyConnection(String dbUrl, String user, Integer poolSize, Integer timeout) throws SQLException {
        LOG.info("Abriendo conexión con parámetros de configuración YAML: URL='{}', Usuario='{}', MaxPoolSize={}, Timeout={}ms",
                maskSensitiveUrl(dbUrl), user, poolSize, timeout);

        Connection connection = getConnection();

        if (!verifyConnection(connection)) {
            try {
                connection.close();
            } catch (SQLException ignored) {
            }
            throw new SQLException("La conexión adquirida de la base de datos no es válida o excedió el tiempo límite.");
        }

        DatabaseMetaData meta = connection.getMetaData();
        String actualUrl = meta.getURL();
        String actualUser = meta.getUserName();
        String dbProduct = meta.getDatabaseProductName() + " " + meta.getDatabaseProductVersion();
        String driver = meta.getDriverName() + " " + meta.getDriverVersion();
        boolean isSsl = actualUrl != null && (actualUrl.toLowerCase().contains("ssl=true") || actualUrl.toLowerCase().contains("sslmode=require"));

        LOG.info("==================================================================");
        LOG.info(" CONEXIÓN A BASE DE DATOS ESTABLECIDA Y VERIFICADA EXITOSAMENTE ");
        LOG.info("==================================================================");
        LOG.info(" - Motor BD:         {}", dbProduct);
        LOG.info(" - Driver JDBC:      {}", driver);
        LOG.info(" - Usuario:          {}", actualUser);
        LOG.info(" - URL Conexión:     {}", maskSensitiveUrl(actualUrl));
        LOG.info(" - Auto-Commit:      {}", connection.getAutoCommit());
        LOG.info(" - Nivel Aislamiento:{}", getIsolationLevelName(connection.getTransactionIsolation()));
        LOG.info(" - Conexión SSL/TLS: {}", isSsl ? "ACTIVA (Cifrado en tránsito - RNF-25)" : "NO ACTIVA (Recomendado sslmode=require para producción)");
        LOG.info("==================================================================");

        return connection;
    }


    /**
     * Verifica internamente la validez de una conexión activa dentro del tiempo de espera.
     *
     * @param connection Conexión SQL a comprobar.
     * @return true si la conexión es válida; false en caso contrario.
     */
    private boolean verifyConnection(Connection connection) {
        if (connection == null) {
            return false;
        }
        try {
            return connection.isValid(VALIDATION_TIMEOUT_SECONDS);
        } catch (SQLException e) {
            LOG.warn("Fallo durante la verificación interna de la conexión: {}", e.getMessage());
            return false;
        }
    }


    private String maskSensitiveUrl(String url) {
        if (url == null) return "N/A";
        return url.replaceAll("(?i)(password=)[^;&]+", "$1*****");
    }

    private String getIsolationLevelName(int level) {
        return switch (level) {
            case Connection.TRANSACTION_READ_UNCOMMITTED -> "READ_UNCOMMITTED";
            case Connection.TRANSACTION_READ_COMMITTED -> "READ_COMMITTED";
            case Connection.TRANSACTION_REPEATABLE_READ -> "REPEATABLE_READ";
            case Connection.TRANSACTION_SERIALIZABLE -> "SERIALIZABLE";
            case Connection.TRANSACTION_NONE -> "NONE";
            default -> "UNKNOWN (" + level + ")";
        };
    }
}
