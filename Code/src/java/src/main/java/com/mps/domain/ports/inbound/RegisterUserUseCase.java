package com.mps.domain.ports.inbound;

import com.mps.domain.model.User;

/**
 * Puerto primario (Driving / Inbound Port) para el caso de uso UC-09a (Registrarse en la Plataforma).
 */
public interface RegisterUserUseCase {

    /**
     * Registra un nuevo usuario en el sistema.
     *
     * @param command datos del usuario (email, rawPassword)
     * @return entidad User persistida con UUID v4 generado
     * @throws com.mps.domain.exception.UserAlreadyExistsException si el email ya existe
     * @throws com.mps.domain.exception.InvalidUserDataException si los datos no cumplen las reglas
     */
    User register(RegisterUserCommand command);
}
