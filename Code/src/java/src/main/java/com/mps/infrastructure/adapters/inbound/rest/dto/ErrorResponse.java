package com.mps.infrastructure.adapters.inbound.rest.dto;

import io.micronaut.core.annotation.Introspected;
import io.micronaut.serde.annotation.Serdeable;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.List;

/**
 * Payload estructurado para respuestas de error semánticas (RNF-15).
 */
@Serdeable
@Introspected
@Schema(description = "Estructura estándar de respuesta de error")
public class ErrorResponse {

    @Schema(description = "Código de estado HTTP", example = "409")
    private int status;

    @Schema(description = "Tipo o nombre del error", example = "Conflict")
    private String error;

    @Schema(description = "Mensaje legible del error", example = "User with email 'usuario@mps.com' already exists")
    private String message;

    @Schema(description = "Detalles o lista de validaciones fallidas")
    private List<String> details;

    @Schema(description = "Marca temporal del error", example = "2026-10-18T20:30:00Z")
    private Instant timestamp;

    public ErrorResponse() {
        this.timestamp = Instant.now();
    }

    public ErrorResponse(int status, String error, String message) {
        this.status = status;
        this.error = error;
        this.message = message;
        this.details = List.of();
        this.timestamp = Instant.now();
    }

    public ErrorResponse(int status, String error, String message, List<String> details) {
        this.status = status;
        this.error = error;
        this.message = message;
        this.details = details != null ? details : List.of();
        this.timestamp = Instant.now();
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public List<String> getDetails() {
        return details;
    }

    public void setDetails(List<String> details) {
        this.details = details;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Instant timestamp) {
        this.timestamp = timestamp;
    }
}
