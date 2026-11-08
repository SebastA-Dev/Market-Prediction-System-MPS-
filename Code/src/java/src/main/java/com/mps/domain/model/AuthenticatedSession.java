package com.mps.domain.model;

import java.util.Objects;

/**
 * Resultado del caso de uso de inicio de sesión: el usuario autenticado y el token de acceso emitido.
 */
public record AuthenticatedSession(
        User user,
        AuthToken token
) {
    public AuthenticatedSession {
        Objects.requireNonNull(user, "User cannot be null");
        Objects.requireNonNull(token, "Token cannot be null");
    }
}
