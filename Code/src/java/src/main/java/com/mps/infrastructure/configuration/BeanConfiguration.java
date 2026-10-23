package com.mps.infrastructure.configuration;

import com.mps.application.service.LoginUserService;
import com.mps.application.service.RegisterUserService;
import com.mps.domain.ports.inbound.LoginUserUseCase;
import com.mps.domain.ports.inbound.RegisterUserUseCase;
import com.mps.domain.ports.outbound.LoginAttemptPort;
import com.mps.domain.ports.outbound.PasswordEncoderPort;
import com.mps.domain.ports.outbound.TokenProviderPort;
import com.mps.domain.ports.outbound.UserRepositoryPort;
import io.micronaut.context.annotation.Factory;
import jakarta.inject.Singleton;

/**
 * Fábrica de configuración de beans para Arquitectura Hexagonal.
 * Instancia y enlaza los casos de uso del dominio con los adaptadores de infraestructura,
 * garantizando que la capa de aplicación y dominio permanezcan 100% puras (RNF-13).
 */
@Factory
public class BeanConfiguration {

    @Singleton
    public RegisterUserUseCase registerUserUseCase(
            UserRepositoryPort userRepository,
            PasswordEncoderPort passwordEncoder
    ) {
        return new RegisterUserService(userRepository, passwordEncoder);
    }

    @Singleton
    public LoginUserUseCase loginUserUseCase(
            UserRepositoryPort userRepository,
            PasswordEncoderPort passwordEncoder,
            TokenProviderPort tokenProvider,
            LoginAttemptPort loginAttempts
    ) {
        return new LoginUserService(userRepository, passwordEncoder, tokenProvider, loginAttempts);
    }
}
