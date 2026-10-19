package com.mps.infrastructure.adapters.inbound.rest.dto;

import io.micronaut.core.annotation.Introspected;
import io.micronaut.serde.annotation.Serdeable;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.UUID;

/**
 * DTO para la respuesta de usuario registrado.
 * Jamás expone contraseñas ni hashes (RNF-26).
 */
@Serdeable
@Introspected
@Schema(description = "Respuesta tras la creación o consulta de usuario")
public class UserResponse {

    @Schema(description = "Identificador único criptográfico (UUID v4)", example = "3fa85f64-5717-4562-b3fc-2c963f66afa6")
    private UUID id;

    @Schema(description = "Correo electrónico del usuario registrado", example = "usuario@mps.com")
    private String email;

    @Schema(description = "Marca temporal de creación de la cuenta", example = "2026-10-18T20:30:00Z")
    private Instant createdAt;

    public UserResponse() {
    }

    public UserResponse(UUID id, String email, Instant createdAt) {
        this.id = id;
        this.email = email;
        this.createdAt = createdAt;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
