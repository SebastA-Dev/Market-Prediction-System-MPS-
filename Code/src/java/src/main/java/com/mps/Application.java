package com.mps;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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

            // // Si se ejecuta en entorno de pruebas ('test'), se omite la configuración de producción
            // if (builder.getActiveEnvironments() != null && builder.getActiveEnvironments().contains("test")) {
            //     LOG.info("Entorno de prueba 'test' detectado; se omite configuración dinámica desde .env");
            //     return;
            // }

            // 1. Localizar y cargar archivo .env centralizado
            File envFile = findDotenvFile();
            Map<String, String> envMap = new HashMap<>();
            if (envFile != null && envFile.exists()) {
                LOG.info("Cargando configuración centralizada desde: {}", envFile.getAbsolutePath());
                envMap = parseDotenv(envFile);
            } else {
                LOG.info("No se encontró archivo .env local. Utilizando variables de entorno del sistema.");
            }

            File envDir = (envFile != null && envFile.exists()) ? envFile.getParentFile() : null;

            // 2. Extraer parámetros de conexión (System.getenv tiene precedencia sobre .env)
            String dbHost = getSetting(envMap, "DB_HOST", "localhost");
            String dbPort = getSetting(envMap, "DB_PORT", "5432");
            String dbName = getSetting(envMap, "DB_NAME", "mps_db");
            String dbUser = getSetting(envMap, "JDBC_USER", getSetting(envMap, "DB_USER", "postgres"));
            String dbPassword = getSetting(envMap, "JDBC_PASSWORD", getSetting(envMap, "DB_PASSWORD", ""));

            String sslMode = getSetting(envMap, "DB_SSL_MODE", getSetting(envMap, "SSL_MODE", ""));
            String sslRootCert = getSetting(envMap, "DB_SSL_ROOT_CERT", getSetting(envMap, "SSL_ROOT_CERT", ""));
            String explicitJdbcUrl = getSetting(envMap, "JDBC_URL", "");

            String poolSize = getSetting(envMap, "DATASOURCES_DEFAULT_MAXIMUM_POOL_SIZE", "20");
            String timeout = getSetting(envMap, "DATASOURCES_DEFAULT_CONNECTION_TIMEOUT", "250");
            String jwtSecret = getSetting(envMap, "JWT_GENERATOR_SIGNATURE_SECRET", "dev-secret-key-must-be-at-least-32-chars-long!");
            String jwtExpiration = getSetting(envMap, "JWT_ACCESS_TOKEN_EXPIRATION", "3600");

            // 3. Construir URL JDBC PostgreSQL con parámetros SSL para AWS RDS
            String finalJdbcUrl;
            if (explicitJdbcUrl != null && !explicitJdbcUrl.isBlank() && explicitJdbcUrl.startsWith("jdbc:postgresql://")) {
                finalJdbcUrl = explicitJdbcUrl;
            } else {
                StringBuilder sb = new StringBuilder("jdbc:postgresql://")
                        .append(dbHost).append(":").append(dbPort).append("/").append(dbName);

                List<String> queryParams = new ArrayList<>();
                if (sslMode != null && !sslMode.isBlank()) {
                    queryParams.add("sslmode=" + sslMode.trim());
                }
                if (sslRootCert != null && !sslRootCert.isBlank()) {
                    String resolvedCert = resolveCertPath(sslRootCert.trim(), envDir);
                    queryParams.add("sslrootcert=" + resolvedCert);
                }
                if (!queryParams.isEmpty()) {
                    sb.append("?").append(String.join("&", queryParams));
                }
                finalJdbcUrl = sb.toString();
            }

            LOG.info("Configurando DataSource PostgreSQL con URL: {}", maskUrl(finalJdbcUrl));

            // 4. Inyectar dinámicamente las propiedades en el builder de Micronaut
            Map<String, Object> props = new HashMap<>();
            props.put("datasources.default.url", finalJdbcUrl);
            props.put("datasources.default.username", dbUser);
            props.put("datasources.default.password", dbPassword);
            props.put("datasources.default.maximum-pool-size", Integer.parseInt(poolSize));
            props.put("datasources.default.connection-timeout", Integer.parseInt(timeout));

            props.put("micronaut.security.token.jwt.signatures.secret.generator.secret", jwtSecret);
            props.put("micronaut.security.token.generator.access-token.expiration", Integer.parseInt(jwtExpiration));

            builder.properties(props);
        }

        //TODO: Manejar un estandar en la ubicacion del .env 
        private static File findDotenvFile() {
            String[] candidatePaths = {
                System.getenv("DOTENV_PATH"),
                System.getProperty("dotenv.path"),
                ".env",
                "../.env",
                "../../.env",
                "../../../.env",
                "Code/.env",
                "../Code/.env",
                "/app/host/.env",
                "/app/.env"
            };

            for (String path : candidatePaths) {
                if (path != null && !path.isBlank()) {
                    File file = new File(path);
                    if (file.exists() && file.isFile()) {
                        return file;
                    }
                }
            }
            return null;
        }

        private static Map<String, String> parseDotenv(File file) {
            Map<String, String> map = new HashMap<>();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) {
                        continue;
                    }
                    int eqIdx = line.indexOf('=');
                    if (eqIdx > 0) {
                        String key = line.substring(0, eqIdx).trim();
                        String val = line.substring(eqIdx + 1).trim();
                        if (((val.startsWith("\"") && val.endsWith("\"")) || (val.startsWith("'") && val.endsWith("'"))) && val.length() >= 2) {
                                val = val.substring(1, val.length() - 1);
                            }
                        
                        map.put(key, val);
                    }
                }
            } catch (IOException e) {
                LOG.error("Error al leer archivo .env: {}", e.getMessage());
            }
            return map;
        }

        private static String getSetting(Map<String, String> envMap, String key, String defaultValue) {
            String sysEnv = System.getenv(key);
            if (sysEnv != null && !sysEnv.isBlank()) {
                return sysEnv.trim();
            }
            String fileVal = envMap.get(key);
            if (fileVal != null && !fileVal.isBlank()) {
                return fileVal.trim();
            }
            return defaultValue;
        }

        private static String resolveCertPath(String certPath, File envDir) {
            File direct = new File(certPath);
            if (direct.exists()) {
                return direct.getAbsolutePath();
            }
            if (envDir != null) {
                File relToEnv = new File(envDir, certPath);
                if (relToEnv.exists()) {
                    return relToEnv.getAbsolutePath();
                }
            }
            File dockerHost = new File("/app/host", certPath);
            if (dockerHost.exists()) {
                return dockerHost.getAbsolutePath();
            }
            File dockerApp = new File("/app", certPath);
            if (dockerApp.exists()) {
                return dockerApp.getAbsolutePath();
            }
            return certPath;
        }

        private static String maskUrl(String url) {
            if (url == null) return "null";
            return url.replaceAll("(?i)(password=)[^&;]*", "$1*****");
        }
    }

    public static void main(String[] args) {
        ApplicationContext context = Micronaut.run(Application.class, args);
        DatabaseConnectionManager connectionManager = context.getBean(DatabaseConnectionManager.class);

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
