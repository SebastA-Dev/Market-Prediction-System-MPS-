package com.mps.domain.exception;

/**
 * Excepción de dominio lanzada cuando se intenta registrar un correo ya existente.
 * Mapea directamente a HTTP 409 Conflict según UC-09a (Paso 3b) y RF-21.
 */
public class UserAlreadyExistsException extends RuntimeException {

    private final String email;

    public UserAlreadyExistsException(String email) {
        super(String.format("User with email '%s' already exists", email));
        this.email = email;
    }

    public String getEmail() {
        return email;
    }
}
