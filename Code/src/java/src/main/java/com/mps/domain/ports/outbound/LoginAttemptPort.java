package com.mps.domain.ports.outbound;

/**
 * Puerto secundario para el control de intentos fallidos de inicio de sesión (protección contra fuerza bruta).
 */
public interface LoginAttemptPort {

    /**
     * @return segundos restantes de bloqueo para el correo, o 0 si no está bloqueado
     */
    long remainingLockSeconds(String email);

    void recordFailure(String email);

    void reset(String email);
}
