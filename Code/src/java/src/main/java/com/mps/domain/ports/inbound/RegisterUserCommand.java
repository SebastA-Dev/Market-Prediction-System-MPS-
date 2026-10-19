package com.mps.domain.ports.inbound;

/**
 * Comando inmutable que transporta los datos requeridos para registrar un usuario.
 */
public record RegisterUserCommand(
        String email,
        String rawPassword
) {
    public RegisterUserCommand {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("Email cannot be null or empty in RegisterUserCommand");
        }
        if (rawPassword == null || rawPassword.isBlank()) {
            throw new IllegalArgumentException("Password cannot be null or empty in RegisterUserCommand");
        }
    }
}
