package com.mps.application.service;

import com.mps.domain.exception.InvalidCredentialsException;
import com.mps.domain.exception.TooManyLoginAttemptsException;
import com.mps.domain.model.AuthToken;
import com.mps.domain.model.AuthenticatedSession;
import com.mps.domain.model.User;
import com.mps.domain.ports.inbound.LoginUserCommand;
import com.mps.domain.ports.inbound.LoginUserUseCase;
import com.mps.domain.ports.outbound.LoginAttemptPort;
import com.mps.domain.ports.outbound.PasswordEncoderPort;
import com.mps.domain.ports.outbound.TokenProviderPort;
import com.mps.domain.ports.outbound.UserRepositoryPort;

import java.util.Objects;
import java.util.Optional;

/**
 * Servicio de aplicación que implementa el inicio de sesión de usuarios registrados (UC-09a).
 * Verifica las credenciales contra el hash PBKDF2 almacenado (RNF-26) y emite un token JWT firmado.
 * Totalmente desacoplado de infraestructura (RNF-13).
 */
public class LoginUserService implements LoginUserUseCase {

    private final UserRepositoryPort userRepository;
    private final PasswordEncoderPort passwordEncoder;
    private final TokenProviderPort tokenProvider;
    private final LoginAttemptPort loginAttempts;

    // Hash de referencia para igualar el tiempo de respuesta cuando el correo no existe (evita enumeración por timing)
    private final String dummyPasswordHash;

    public LoginUserService(
            UserRepositoryPort userRepository,
            PasswordEncoderPort passwordEncoder,
            TokenProviderPort tokenProvider,
            LoginAttemptPort loginAttempts
    ) {
        this.userRepository = Objects.requireNonNull(userRepository, "UserRepositoryPort cannot be null");
        this.passwordEncoder = Objects.requireNonNull(passwordEncoder, "PasswordEncoderPort cannot be null");
        this.tokenProvider = Objects.requireNonNull(tokenProvider, "TokenProviderPort cannot be null");
        this.loginAttempts = Objects.requireNonNull(loginAttempts, "LoginAttemptPort cannot be null");
        this.dummyPasswordHash = passwordEncoder.encode("dummy-password-for-timing-equalization");
    }

    @Override
    public AuthenticatedSession login(LoginUserCommand command) {
        if (command == null) {
            throw new InvalidCredentialsException();
        }

        String normalizedEmail = command.email().trim().toLowerCase();

        // Bloqueo temporal tras intentos fallidos consecutivos (protección contra fuerza bruta)
        long remainingLock = loginAttempts.remainingLockSeconds(normalizedEmail);
        if (remainingLock > 0) {
            throw new TooManyLoginAttemptsException(remainingLock);
        }

        Optional<User> user = userRepository.findByEmail(normalizedEmail);

        // Siempre se verifica un hash, exista o no la cuenta, para no revelar qué correos están registrados
        String storedHash = user.map(User::getPasswordHash).orElse(dummyPasswordHash);
        boolean passwordMatches = passwordEncoder.matches(command.rawPassword(), storedHash);

        if (user.isEmpty() || !passwordMatches) {
            loginAttempts.recordFailure(normalizedEmail);
            throw new InvalidCredentialsException();
        }

        loginAttempts.reset(normalizedEmail);

        AuthToken token = tokenProvider.issueToken(user.get());
        return new AuthenticatedSession(user.get(), token);
    }
}
