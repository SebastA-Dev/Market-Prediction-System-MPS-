package com.mps.domain.exception;

/**
 * Excepción de dominio lanzada cuando el correo o la contraseña no son válidos durante el inicio de sesión.
 * El mensaje es deliberadamente genérico para no revelar si la cuenta existe (enumeración de usuarios).
 * Mapea a HTTP 401 Unauthorized.
 */
public class InvalidCredentialsException extends RuntimeException {

    public InvalidCredentialsException() {
        super("Invalid email or password");
    }
}
