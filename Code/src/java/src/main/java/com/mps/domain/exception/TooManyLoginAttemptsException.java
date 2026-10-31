package com.mps.domain.exception;

/**
 * Excepción de dominio lanzada cuando una cuenta acumula demasiados intentos fallidos de inicio de sesión
 * y queda bloqueada temporalmente (protección contra fuerza bruta).
 * Mapea a HTTP 429 Too Many Requests.
 */
public class TooManyLoginAttemptsException extends RuntimeException {

    private final long retryAfterSeconds;

    public TooManyLoginAttemptsException(long retryAfterSeconds) {
        super("Too many failed login attempts. Try again later");
        this.retryAfterSeconds = retryAfterSeconds;
    }

    public long getRetryAfterSeconds() {
        return retryAfterSeconds;
    }
}
