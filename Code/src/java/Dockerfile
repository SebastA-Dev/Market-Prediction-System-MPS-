# ==============================================================================
# Dockerfile para Servicio Java (Micronaut - JDK 21)
# ==============================================================================

# 1. Etapa de compilación con Maven Wrapper
FROM eclipse-temurin:21-jdk-jammy AS builder

WORKDIR /build

# Instalar utilidades básicas como dos2unix y maven (como fallback seguro)
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix maven && rm -rf /var/lib/apt/lists/*

# Copiar archivos de Maven y configuración de dependencias
COPY .mvn/ .mvn/
COPY mvnw pom.xml ./

# Asegurar formato Unix (LF) y permisos de ejecución para el wrapper
RUN dos2unix ./mvnw && chmod +x ./mvnw

# Descargar dependencias en caché
RUN ./mvnw dependency:go-offline -DskipTests -Denforcer.skip=true -B || mvn dependency:go-offline -DskipTests -Denforcer.skip=true -B || true

# Copiar código fuente y empaquetar
COPY src/ ./src/
RUN ./mvnw clean package -DskipTests -Denforcer.skip=true -B || mvn clean package -DskipTests -Denforcer.skip=true -B

# 2. Etapa de ejecución liviana (JRE 21)
FROM eclipse-temurin:21-jre-jammy

WORKDIR /app

# Crear usuario sin privilegios para ejecución segura
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copiar el jar empaquetado desde la etapa de compilación
COPY --from=builder /build/target/java-*.jar /app/application.jar

# Variables de entorno por defecto
ENV MICRONAUT_ENVIRONMENTS=prod \
    JAVA_OPTS="-Xms256m -Xmx512m -XX:+UseG1GC"

EXPOSE 8080

USER appuser

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/application.jar"]
