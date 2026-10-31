package com.mps.infrastructure.adapters.inbound.rest;

import com.mps.infrastructure.adapters.inbound.rest.dto.RegisterUserRequest;
import com.mps.infrastructure.adapters.inbound.rest.dto.UserResponse;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.http.client.exceptions.HttpClientResponseException;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@MicronautTest
@DisplayName("Pruebas de Integración HTTP: UserController (/api/v1/users)")
class UserControllerTest {

    @Inject
    @Client("/")
    HttpClient client;

    @Test
    @DisplayName("POST /api/v1/users debe responder 201 Created y retornar el usuario registrado")
    void shouldRegisterUserSuccessfully() {
        String uniqueEmail = "testuser_" + System.currentTimeMillis() + "@mps.com";
        RegisterUserRequest request = new RegisterUserRequest(uniqueEmail, "StrongPassword123*");

        HttpResponse<UserResponse> response = client.toBlocking().exchange(
                HttpRequest.POST("/api/v1/users", request),
                UserResponse.class
        );

        assertEquals(HttpStatus.CREATED, response.status());
        UserResponse body = response.body();
        assertNotNull(body);
        assertNotNull(body.getId());
        assertEquals(uniqueEmail, body.getEmail());
        assertNotNull(body.getCreatedAt());
    }

    @Test
    @DisplayName("POST /api/v1/users con correo duplicado debe responder 409 Conflict")
    void shouldReturn409WhenEmailAlreadyExists() {
        String duplicateEmail = "conflict_" + System.currentTimeMillis() + "@mps.com";
        RegisterUserRequest request = new RegisterUserRequest(duplicateEmail, "SecretPass123!");

        // Primer registro exitoso
        HttpResponse<UserResponse> firstResponse = client.toBlocking().exchange(
                HttpRequest.POST("/api/v1/users", request),
                UserResponse.class
        );
        assertEquals(HttpStatus.CREATED, firstResponse.status());

        // Segundo intento con el mismo email -> debe retornar 409 Conflict
        HttpClientResponseException exception = assertThrows(
                HttpClientResponseException.class,
                () -> client.toBlocking().exchange(
                        HttpRequest.POST("/api/v1/users", request),
                        UserResponse.class
                )
        );

        assertEquals(HttpStatus.CONFLICT, exception.getStatus());
    }

    @Test
    @DisplayName("POST /api/v1/users con email inválido debe responder 400 Bad Request")
    void shouldReturn400ForInvalidEmail() {
        RegisterUserRequest request = new RegisterUserRequest("not-an-email", "ValidPassword123!");

        HttpClientResponseException exception = assertThrows(
                HttpClientResponseException.class,
                () -> client.toBlocking().exchange(
                        HttpRequest.POST("/api/v1/users", request),
                        UserResponse.class
                )
        );

        assertEquals(HttpStatus.BAD_REQUEST, exception.getStatus());
    }

    @Test
    @DisplayName("POST /api/v1/users con contraseña corta (< 8 caracteres) debe responder 400 Bad Request")
    void shouldReturn400ForShortPassword() {
        RegisterUserRequest request = new RegisterUserRequest("valid@mps.com", "123");

        HttpClientResponseException exception = assertThrows(
                HttpClientResponseException.class,
                () -> client.toBlocking().exchange(
                        HttpRequest.POST("/api/v1/users", request),
                        UserResponse.class
                )
        );

        assertEquals(HttpStatus.BAD_REQUEST, exception.getStatus());
    }
}
