package com.mps;

import java.sql.Connection;
import java.sql.SQLException;

import org.jspecify.annotations.NonNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.mps.infrastructure.adapters.outbound.persistence.connection.DatabaseConnectionManager;

import io.micronaut.context.ApplicationContext;
import io.micronaut.context.ApplicationContextBuilder;
import io.micronaut.context.ApplicationContextConfigurer;
import io.micronaut.context.annotation.ContextConfigurer;
import io.micronaut.runtime.Micronaut;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.security.SecurityScheme;

@OpenAPIDefinition(
    info = @Info(
            title = "java",
            version = "0.0"
    )
)
@SecurityScheme(
    name = "BearerAuth",
    type = SecuritySchemeType.HTTP,
    scheme = "bearer",
    bearerFormat = "JWT"
)
public class Application {

    private static final Logger LOG = LoggerFactory.getLogger(Application.class);

    @ContextConfigurer
    public static class Configurer implements ApplicationContextConfigurer {
        @Override
        public void configure(@NonNull ApplicationContextBuilder builder) {
            builder.defaultEnvironments("dev");
        }
    }

    public static void main(String[] args) {
        ApplicationContext context = Micronaut.run(Application.class, args);
        DatabaseConnectionManager connectionManager = context.getBean(DatabaseConnectionManager.class);

        // Parámetros resueltos de la configuración YAML (application.yml procesado por snakeyaml)
        String dbUrl = context.getProperty("datasources.default.url", String.class)
                .orElse("jdbc:postgresql://localhost:5432/mps_db");
        String dbUser = context.getProperty("datasources.default.username", String.class)
                .orElse("postgres");
        Integer poolSize = context.getProperty("datasources.default.maximum-pool-size", Integer.class)
                .orElse(20);
        Integer timeout = context.getProperty("datasources.default.connection-timeout", Integer.class)
                .orElse(250);

        try (Connection connection = connectionManager.openAndVerifyConnection(dbUrl, dbUser, poolSize, timeout)) {
            LOG.info("Conexión inicial a la base de datos abierta y verificada exitosamente.");
        } catch (SQLException e) {
            LOG.error("No se pudo abrir la conexión a la base de datos al iniciar la aplicación: {}", e.getMessage());
        }
    }
}