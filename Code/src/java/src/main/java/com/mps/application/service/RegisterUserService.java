package com.mps.application.service;

import com.mps.domain.exception.InvalidUserDataException;
import com.mps.domain.exception.UserAlreadyExistsException;
import com.mps.domain.model.User;
import com.mps.domain.ports.inbound.RegisterUserCommand;
import com.mps.domain.ports.inbound.RegisterUserUseCase;
import com.mps.domain.ports.outbound.PasswordEncoderPort;
import com.mps.domain.ports.outbound.UserRepositoryPort;

import java.util.Objects;

/**
 * Servicio de aplicación que implementa el caso de uso UC-09a (Registrarse en la Plataforma).
 * Orquesta las reglas de negocio, validaciones de unicidad y persistencia a través de puertos.
 * Totalmente desacoplado de infraestructura (RNF-13).
 */
public class RegisterUserService implements RegisterUserUseCase {

    private final UserRepositoryPort userRepository;
    private final PasswordEncoderPort passwordEncoder;

    public RegisterUserService(UserRepositoryPort userRepository, PasswordEncoderPort passwordEncoder) {
        this.userRepository = Objects.requireNonNull(userRepository, "UserRepositoryPort cannot be null");
        this.passwordEncoder = Objects.requireNonNull(passwordEncoder, "PasswordEncoderPort cannot be null");
    }

    @Override
    public User register(RegisterUserCommand command) {
        if (command == null) {
            throw new InvalidUserDataException("RegisterUserCommand cannot be null");
        }

        String rawEmail = command.email();
        if (rawEmail == null || rawEmail.trim().isEmpty()) {
            throw new InvalidUserDataException("Email is mandatory for user registration");
        }
        String normalizedEmail = rawEmail.trim().toLowerCase();

        String rawPassword = command.rawPassword();
        if (rawPassword == null || rawPassword.trim().isEmpty()) {
            throw new InvalidUserDataException("Password is mandatory for user registration");
        }
        if (rawPassword.length() < 8) {
            throw new InvalidUserDataException("Password must contain at least 8 characters");
        }

        // Validación de unicidad de cuenta en BD (UC-09a, Paso 3b)
        if (userRepository.existsByEmail(normalizedEmail)) {
            throw new UserAlreadyExistsException(normalizedEmail);
        }

        // Cifrado criptográfico con salting (RNF-26)
        String hashedPassword = passwordEncoder.encode(rawPassword);

        // Creación de entidad de dominio con generación de UUID v4 criptográfico (RF-21, RNF-23)
        User newUser = User.create(normalizedEmail, hashedPassword);

        // Persistencia a través del puerto secundario
        return userRepository.save(newUser);
    }
}
