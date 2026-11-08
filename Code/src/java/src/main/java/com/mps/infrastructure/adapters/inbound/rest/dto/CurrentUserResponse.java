package com.mps.infrastructure.adapters.inbound.rest.dto;

import io.micronaut.core.annotation.Introspected;
import io.micronaut.serde.annotation.Serdeable;
import io.swagger.v3.oas.annotations.media.Schema;

/**
 * DTO con la identidad extraída de un JWT válido.
 */
@Serdeable
@Introspected
@Schema(description = "Identidad del usuario autenticado según su token")
public class CurrentUserResponse {

    @Schema(description = "Identificador único del usuario (claim 'sub')", example = "3fa85f64-5717-4562-b3fc-2c963f66afa6")
    private String id;

    @Schema(description = "Correo electrónico del usuario", example = "usuario@mps.com")
    private String email;

    public CurrentUserResponse() {
    }

    public CurrentUserResponse(String id, String email) {
        this.id = id;
        this.email = email;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
