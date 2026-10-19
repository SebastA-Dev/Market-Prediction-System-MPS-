package com.mps.domain.exception;

/**
 * Excepción de dominio lanzada ante violaciones de invariantes y reglas de negocio del modelo User.
 * Mapea a HTTP 400 Bad Request.
 */
public class InvalidUserDataException extends RuntimeException {

    public InvalidUserDataException(String message) {
        super(message);
    }

    public InvalidUserDataException(String message, Throwable cause) {
        super(message, cause);
    }
}
