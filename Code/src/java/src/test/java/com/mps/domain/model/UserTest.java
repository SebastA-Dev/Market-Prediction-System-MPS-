package com.mps.domain.model;

import com.mps.domain.exception.InvalidUserDataException;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.time.Instant;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Pruebas Unitarias del Modelo de Dominio: User")
class UserTest {

    @Test
    @DisplayName("Debe crear un usuario válido con UUID y marca temporal generada")
    void shouldCreateValidUserViaFactory() {
        String email = "trader@mps.com";
        String passwordHash = "$pbkdf2-sha256$65536$salt$hash";

        User user = User.create(email, passwordHash);

        assertNotNull(user);
        assertNotNull(user.getId());
        assertEquals("trader@mps.com", user.getEmail());
        assertEquals(passwordHash, user.getPasswordHash());
        assertNotNull(user.getCreatedAt());
        assertTrue(user.getCreatedAt().isBefore(Instant.now().plusSeconds(1)));
    }

    @ParameterizedTest
    @ValueSource(strings = {"invalid-email", "trader@", "@mps.com", "trader@mps", "trader.com"})
    @DisplayName("Debe lanzar InvalidUserDataException si el correo tiene sintaxis inválida")
    void shouldThrowExceptionWhenEmailIsInvalid(String invalidEmail) {
        assertThrows(InvalidUserDataException.class, () ->
                User.create(invalidEmail, "someHash123")
        );
    }

    @Test
    @DisplayName("Debe lanzar InvalidUserDataException cuando el correo o contraseña son nulos o vacíos")
    void shouldThrowExceptionWhenFieldsAreNullOrBlank() {
        assertThrows(InvalidUserDataException.class, () -> User.create(null, "hash"));
        assertThrows(InvalidUserDataException.class, () -> User.create("   ", "hash"));
        assertThrows(InvalidUserDataException.class, () -> User.create("valid@mps.com", null));
        assertThrows(InvalidUserDataException.class, () -> User.create("valid@mps.com", "   "));
    }

    @Test
    @DisplayName("Dos usuarios con el mismo ID deben ser considerados iguales (identidad de entidad)")
    void shouldEqualBasedOnId() {
        UUID id = UUID.randomUUID();
        Instant now = Instant.now();
        User u1 = new User(id, "user1@mps.com", "hash1", now);
        User u2 = new User(id, "user2@mps.com", "hash2", now);

        assertEquals(u1, u2);
        assertEquals(u1.hashCode(), u2.hashCode());
    }
}
