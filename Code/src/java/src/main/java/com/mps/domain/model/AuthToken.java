package com.mps.domain.model;

import java.util.Objects;

/**
 * Value object inmutable que representa un token de acceso emitido tras una autenticación exitosa.
 * Agnóstico del formato concreto (JWT) y de la librería que lo firma.
 */
public record AuthToken(
        String accessToken,
        String tokenType,
        long expiresInSeconds
) {
    public AuthToken {
        Objects.requireNonNull(accessToken, "Access token cannot be null");
        Objects.requireNonNull(tokenType, "Token type cannot be null");
        if (expiresInSeconds <= 0) {
            throw new IllegalArgumentException("Token expiration must be positive");
        }
    }
}
