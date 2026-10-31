package com.mps.application.service;

import com.mps.domain.exception.InvalidCredentialsException;
import com.mps.domain.exception.TooManyLoginAttemptsException;
import com.mps.domain.model.AuthToken;
import com.mps.domain.model.AuthenticatedSession;
import com.mps.domain.model.User;
import com.mps.domain.ports.inbound.LoginUserCommand;
import com.mps.domain.ports.outbound.LoginAttemptPort;
import com.mps.domain.ports.outbound.TokenProviderPort;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Pruebas Unitarias Aisladas (Hexagonal): LoginUserService")
class LoginUserServiceTest {

    private RegisterUserServiceTest.InMemoryUserRepository fakeRepository;
    private RegisterUserServiceTest.FakePasswordEncoder fakePasswordEncoder;
    private FakeLoginAttempts fakeLoginAttempts;
    private LoginUserService service;
    private User existingUser;

    @BeforeEach
    void setUp() {
        fakeRepository = new RegisterUserServiceTest.InMemoryUserRepository();
        fakePasswordEncoder = new RegisterUserServiceTest.FakePasswordEncoder();
        fakeLoginAttempts = new FakeLoginAttempts(3);
        service = new LoginUserService(fakeRepository, fakePasswordEncoder, new FakeTokenProvider(), fakeLoginAttempts);

        existingUser = fakeRepository.save(User.create("trader@mps.com", fakePasswordEncoder.encode("SecurePass123!")));
    }

    @Test
    @DisplayName("Debe autenticar con credenciales válidas y emitir un token para el usuario")
    void shouldLoginSuccessfully() {
        AuthenticatedSession session = service.login(new LoginUserCommand("trader@mps.com", "SecurePass123!"));

        assertEquals(existingUser, session.user());
        assertEquals("TOKEN_" + existingUser.getId(), session.token().accessToken());
        assertEquals("Bearer", session.token().tokenType());
    }

    @Test
    @DisplayName("Debe normalizar el email (trim + minúsculas) antes de buscar la cuenta")
    void shouldNormalizeEmail() {
        AuthenticatedSession session = service.login(new LoginUserCommand("  TRADER@MPS.COM ", "SecurePass123!"));

        assertEquals(existingUser, session.user());
    }

    @Test
    @DisplayName("Debe lanzar InvalidCredentialsException (401) con contraseña incorrecta")
    void shouldRejectWrongPassword() {
        assertThrows(InvalidCredentialsException.class,
                () -> service.login(new LoginUserCommand("trader@mps.com", "WrongPass123!")));
    }

    @Test
    @DisplayName("Debe lanzar el mismo error genérico si el correo no existe (sin enumeración de usuarios)")
    void shouldRejectUnknownEmailWithSameError() {
        InvalidCredentialsException unknown = assertThrows(InvalidCredentialsException.class,
                () -> service.login(new LoginUserCommand("ghost@mps.com", "SecurePass123!")));
        InvalidCredentialsException wrongPassword = assertThrows(InvalidCredentialsException.class,
                () -> service.login(new LoginUserCommand("trader@mps.com", "WrongPass123!")));

        assertEquals(wrongPassword.getMessage(), unknown.getMessage());
    }

    @Test
    @DisplayName("Debe bloquear la cuenta tras superar el máximo de intentos fallidos (429)")
    void shouldLockAfterTooManyFailures() {
        for (int i = 0; i < 3; i++) {
            assertThrows(InvalidCredentialsException.class,
                    () -> service.login(new LoginUserCommand("trader@mps.com", "WrongPass123!")));
        }

        // Incluso con la contraseña correcta, la cuenta sigue bloqueada
        assertThrows(TooManyLoginAttemptsException.class,
                () -> service.login(new LoginUserCommand("trader@mps.com", "SecurePass123!")));
    }

    @Test
    @DisplayName("Debe reiniciar el contador de fallos tras un inicio de sesión exitoso")
    void shouldResetFailuresAfterSuccess() {
        assertThrows(InvalidCredentialsException.class,
                () -> service.login(new LoginUserCommand("trader@mps.com", "WrongPass123!")));

        service.login(new LoginUserCommand("trader@mps.com", "SecurePass123!"));

        assertEquals(0, fakeLoginAttempts.failures("trader@mps.com"));
    }

    // --- Dobles de prueba ---

    static class FakeTokenProvider implements TokenProviderPort {
        @Override
        public AuthToken issueToken(User user) {
            return new AuthToken("TOKEN_" + user.getId(), "Bearer", 3600);
        }
    }

    static class FakeLoginAttempts implements LoginAttemptPort {
        private final int maxFailures;
        private final Map<String, Integer> failuresByEmail = new HashMap<>();

        FakeLoginAttempts(int maxFailures) {
            this.maxFailures = maxFailures;
        }

        int failures(String email) {
            return failuresByEmail.getOrDefault(email, 0);
        }

        @Override
        public long remainingLockSeconds(String email) {
            return failures(email) >= maxFailures ? 60 : 0;
        }

        @Override
        public void recordFailure(String email) {
            failuresByEmail.merge(email, 1, Integer::sum);
        }

        @Override
        public void reset(String email) {
            failuresByEmail.remove(email);
        }
    }
}
