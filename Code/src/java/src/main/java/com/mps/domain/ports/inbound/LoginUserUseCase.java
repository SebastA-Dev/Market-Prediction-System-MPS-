package com.mps.domain.ports.inbound;

import com.mps.domain.model.AuthenticatedSession;

/**
 * Puerto primario (Driving / Inbound Port) para el caso de uso de inicio de sesión
 * (precondición de UC-09b: "El usuario se encuentra autenticado en el sistema").
 */
public interface LoginUserUseCase {

    /**
     * Autentica al usuario con sus credenciales y emite un token de acceso.
     *
     * @param command credenciales del usuario (email, rawPassword)
     * @return sesión autenticada con el usuario y su token de acceso firmado
     * @throws com.mps.domain.exception.InvalidCredentialsException si el correo o la contraseña no coinciden
     * @throws com.mps.domain.exception.TooManyLoginAttemptsException si la cuenta está bloqueada temporalmente
     */
    AuthenticatedSession login(LoginUserCommand command);
}
