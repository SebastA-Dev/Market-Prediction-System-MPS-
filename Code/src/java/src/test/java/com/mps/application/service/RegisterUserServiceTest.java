package com.mps.application.service;

import com.mps.domain.exception.InvalidUserDataException;
import com.mps.domain.exception.UserAlreadyExistsException;
import com.mps.domain.model.User;
import com.mps.domain.ports.inbound.RegisterUserCommand;
import com.mps.domain.ports.outbound.PasswordEncoderPort;
import com.mps.domain.ports.outbound.UserRepositoryPort;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Pruebas Unitarias Aisladas (Hexagonal): RegisterUserService")
class RegisterUserServiceTest {

    private InMemoryUserRepository fakeRepository;
    private FakePasswordEncoder fakePasswordEncoder;
    private RegisterUserService service;

    @BeforeEach
    void setUp() {
        fakeRepository = new InMemoryUserRepository();
        fakePasswordEncoder = new FakePasswordEncoder();
        service = new RegisterUserService(fakeRepository, fakePasswordEncoder);
    }

    @Test
    @DisplayName("Debe registrar exitosamente un usuario nuevo con UUID y contraseña cifrada")
    void shouldRegisterNewUserSuccessfully() {
        RegisterUserCommand command = new RegisterUserCommand("newtrader@mps.com", "SecurePass123!");

        User registered = service.register(command);

        assertNotNull(registered);
        assertNotNull(registered.getId());
        assertEquals("newtrader@mps.com", registered.getEmail());
        assertEquals("ENCODED_SecurePass123!", registered.getPasswordHash());
        assertNotNull(registered.getCreatedAt());

        // Verificar que fue persistido en el repositorio
        assertTrue(fakeRepository.existsByEmail("newtrader@mps.com"));
        Optional<User> found = fakeRepository.findById(registered.getId());
        assertTrue(found.isPresent());
        assertEquals(registered, found.get());
    }

    @Test
    @DisplayName("Debe lanzar UserAlreadyExistsException (409) cuando el email ya está registrado")
    void shouldThrowConflictWhenEmailAlreadyExists() {
        // Pre-poblar usuario existente
        User existingUser = User.create("existing@mps.com", "someHash");
        fakeRepository.save(existingUser);

        RegisterUserCommand command = new RegisterUserCommand("existing@mps.com", "AnotherPassword999");

        UserAlreadyExistsException exception = assertThrows(
                UserAlreadyExistsException.class,
                () -> service.register(command)
        );

        assertTrue(exception.getMessage().contains("existing@mps.com"));
    }

    @Test
    @DisplayName("Debe normalizar el email a minúsculas y trim antes de evaluar unicidad y guardar")
    void shouldNormalizeEmail() {
        RegisterUserCommand command = new RegisterUserCommand("   UPPERCASE@MPS.COM  ", "ValidPass123");

        User registered = service.register(command);

        assertEquals("uppercase@mps.com", registered.getEmail());
        assertTrue(fakeRepository.existsByEmail("uppercase@mps.com"));
    }

    @Test
    @DisplayName("Debe lanzar InvalidUserDataException si la contraseña tiene menos de 8 caracteres")
    void shouldThrowExceptionWhenPasswordIsTooShort() {
        RegisterUserCommand command = new RegisterUserCommand("trader@mps.com", "short");

        assertThrows(InvalidUserDataException.class, () -> service.register(command));
    }

    // --- Dobles de prueba (Fakes en memoria según RNF-14 / RF-29) ---

    static class InMemoryUserRepository implements UserRepositoryPort {
        private final Map<UUID, User> databaseById = new HashMap<>();
        private final Map<String, UUID> indexByEmail = new HashMap<>();

        @Override
        public User save(User user) {
            databaseById.put(user.getId(), user);
            indexByEmail.put(user.getEmail(), user.getId());
            return user;
        }

        @Override
        public Optional<User> findById(UUID id) {
            return Optional.ofNullable(databaseById.get(id));
        }

        @Override
        public Optional<User> findByEmail(String email) {
            UUID id = indexByEmail.get(email);
            if (id == null) return Optional.empty();
            return Optional.ofNullable(databaseById.get(id));
        }

        @Override
        public boolean existsByEmail(String email) {
            return indexByEmail.containsKey(email);
        }
    }

    static class FakePasswordEncoder implements PasswordEncoderPort {
        @Override
        public String encode(String rawPassword) {
            return "ENCODED_" + rawPassword;
        }

        @Override
        public boolean matches(String rawPassword, String encodedPassword) {
            return ("ENCODED_" + rawPassword).equals(encodedPassword);
        }
    }
}
