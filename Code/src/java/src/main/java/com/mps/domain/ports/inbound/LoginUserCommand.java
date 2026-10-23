package com.mps.domain.ports.inbound;

/**
 * Comando inmutable que transporta las credenciales requeridas para iniciar sesión.
 */
public record LoginUserCommand(
        String email,
        String rawPassword
) {
    public LoginUserCommand {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("Email cannot be null or empty in LoginUserCommand");
        }
        if (rawPassword == null || rawPassword.isBlank()) {
            throw new IllegalArgumentException("Password cannot be null or empty in LoginUserCommand");
        }
    }

    /**
     * Evita que la contraseña en texto plano termine en logs o trazas.
     */
    @Override
    public String toString() {
        return "LoginUserCommand{email='" + email + "', rawPassword='****'}";
    }
}
