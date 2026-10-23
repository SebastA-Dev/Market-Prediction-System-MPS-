package com.mps.infrastructure.adapters.inbound.rest;

import com.mps.infrastructure.adapters.inbound.rest.dto.CurrentUserResponse;
import com.mps.infrastructure.adapters.inbound.rest.dto.LoginRequest;
import com.mps.infrastructure.adapters.inbound.rest.dto.LoginResponse;
import com.mps.infrastructure.adapters.inbound.rest.dto.RegisterUserRequest;
import com.mps.infrastructure.adapters.inbound.rest.dto.UserResponse;
import io.micronaut.http.HttpHeaders;
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

import java.util.Base64;

import static org.junit.jupiter.api.Assertions.*;

@MicronautTest
@DisplayName("Pruebas de Integración HTTP: AuthController (/api/v1/auth)")
class AuthControllerTest {

    private static final String PASSWORD = "StrongPassword123*";

    @Inject
    @Client("/")
    HttpClient client;

    private String registerUniqueUser(String prefix) {
        String email = prefix + "_" + System.nanoTime() + "@mps.com";
        HttpResponse<UserResponse> response = client.toBlocking().exchange(
                HttpRequest.POST("/api/v1/users", new RegisterUserRequest(email, PASSWORD)),
                UserResponse.class
        );
        assertEquals(HttpStatus.CREATED, response.status());
        return email;
    }

    private HttpResponse<LoginResponse> login(String email, String password) {
        return client.toBlocking().exchange(
                HttpRequest.POST("/api/v1/auth/login", new LoginRequest(email, password)),
                LoginResponse.class
        );
    }

    private HttpStatus loginExpectingError(String email, String password) {
        HttpClientResponseException exception = assertThrows(
                HttpClientResponseException.class,
                () -> login(email, password)
        );
        return exception.getStatus();
    }

    @Test
    @DisplayName("POST /api/v1/auth/login debe responder 200 con un JWT Bearer firmado")
    void shouldLoginAndReturnJwt() {
        String email = registerUniqueUser("login");

        HttpResponse<LoginResponse> response = login(email, PASSWORD);

        assertEquals(HttpStatus.OK, response.status());
        assertEquals("no-store", response.header(HttpHeaders.CACHE_CONTROL));
        LoginResponse body = response.body();
        assertNotNull(body);
        assertEquals("Bearer", body.getTokenType());
        assertEquals(3600, body.getExpiresIn());
        assertEquals(email, body.getUser().getEmail());
        // Un JWT firmado (JWS) tiene tres segmentos: header.payload.signature
        assertEquals(3, body.getAccessToken().split("\\.").length);
    }

    @Test
    @DisplayName("POST /api/v1/auth/login con contraseña incorrecta debe responder 401")
    void shouldReturn401ForWrongPassword() {
        String email = registerUniqueUser("wrongpass");

        assertEquals(HttpStatus.UNAUTHORIZED, loginExpectingError(email, "NotThePassword1!"));
    }

    @Test
    @DisplayName("POST /api/v1/auth/login con correo no registrado debe responder 401")
    void shouldReturn401ForUnknownEmail() {
        assertEquals(HttpStatus.UNAUTHORIZED, loginExpectingError("ghost_" + System.nanoTime() + "@mps.com", PASSWORD));
    }

    @Test
    @DisplayName("POST /api/v1/auth/login con email inválido debe responder 400")
    void shouldReturn400ForInvalidEmail() {
        assertEquals(HttpStatus.BAD_REQUEST, loginExpectingError("not-an-email", PASSWORD));
    }

    @Test
    @DisplayName("POST /api/v1/auth/login debe responder 429 tras 5 intentos fallidos")
    void shouldReturn429AfterTooManyFailures() {
        String email = registerUniqueUser("bruteforce");

        for (int i = 0; i < 5; i++) {
            assertEquals(HttpStatus.UNAUTHORIZED, loginExpectingError(email, "NotThePassword1!"));
        }

        HttpClientResponseException exception = assertThrows(
                HttpClientResponseException.class,
                () -> login(email, PASSWORD)
        );
        assertEquals(HttpStatus.TOO_MANY_REQUESTS, exception.getStatus());
        assertNotNull(exception.getResponse().header(HttpHeaders.RETRY_AFTER));
    }

    @Test
    @DisplayName("GET /api/v1/auth/me con un JWT válido debe devolver la identidad del usuario")
    void shouldReturnCurrentUserWithValidToken() {
        String email = registerUniqueUser("me");
        LoginResponse login = login(email, PASSWORD).body();

        HttpResponse<CurrentUserResponse> response = client.toBlocking().exchange(
                HttpRequest.GET("/api/v1/auth/me").bearerAuth(login.getAccessToken()),
                CurrentUserResponse.class
        );

        assertEquals(HttpStatus.OK, response.status());
        assertEquals(login.getUser().getId().toString(), response.body().getId());
        assertEquals(email, response.body().getEmail());
    }

    @Test
    @DisplayName("GET /api/v1/auth/me sin token debe responder 401")
    void shouldReturn401WithoutToken() {
        HttpClientResponseException exception = assertThrows(
                HttpClientResponseException.class,
                () -> client.toBlocking().exchange(HttpRequest.GET("/api/v1/auth/me"), CurrentUserResponse.class)
        );

        assertEquals(HttpStatus.UNAUTHORIZED, exception.getStatus());
    }

    @Test
    @DisplayName("GET /api/v1/auth/me con un JWT manipulado debe responder 401")
    void shouldReturn401WithTamperedToken() {
        String email = registerUniqueUser("tampered");
        String token = login(email, PASSWORD).body().getAccessToken();

        // Se altera el payload (sub) manteniendo la firma original
        String[] parts = token.split("\\.");
        String forgedPayload = Base64.getUrlEncoder().withoutPadding()
                .encodeToString("{\"sub\":\"00000000-0000-0000-0000-000000000000\",\"email\":\"admin@mps.com\"}".getBytes());
        String forgedToken = parts[0] + "." + forgedPayload + "." + parts[2];

        HttpClientResponseException exception = assertThrows(
                HttpClientResponseException.class,
                () -> client.toBlocking().exchange(
                        HttpRequest.GET("/api/v1/auth/me").bearerAuth(forgedToken),
                        CurrentUserResponse.class
                )
        );

        assertEquals(HttpStatus.UNAUTHORIZED, exception.getStatus());
    }
}
