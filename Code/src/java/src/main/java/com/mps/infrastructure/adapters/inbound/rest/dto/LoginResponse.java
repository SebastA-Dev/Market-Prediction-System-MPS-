package com.mps.infrastructure.adapters.inbound.rest.dto;

import io.micronaut.core.annotation.Introspected;
import io.micronaut.serde.annotation.Serdeable;
import io.swagger.v3.oas.annotations.media.Schema;

/**
 * DTO para la respuesta de inicio de sesión exitoso.
 * Contiene el JWT firmado que el cliente debe enviar en la cabecera 'Authorization: Bearer <token>'.
 */
@Serdeable
@Introspected
@Schema(description = "Token de acceso emitido tras una autenticación exitosa")
public class LoginResponse {

    @Schema(description = "JWT firmado (HS256)", example = "eyJhbGciOiJIUzI1NiJ9...")
    private String accessToken;

    @Schema(description = "Tipo de token", example = "Bearer")
    private String tokenType;

    @Schema(description = "Segundos hasta la expiración del token", example = "3600")
    private long expiresIn;

    @Schema(description = "Usuario autenticado")
    private UserResponse user;

    public LoginResponse() {
    }

    public LoginResponse(String accessToken, String tokenType, long expiresIn, UserResponse user) {
        this.accessToken = accessToken;
        this.tokenType = tokenType;
        this.expiresIn = expiresIn;
        this.user = user;
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getTokenType() {
        return tokenType;
    }

    public void setTokenType(String tokenType) {
        this.tokenType = tokenType;
    }

    public long getExpiresIn() {
        return expiresIn;
    }

    public void setExpiresIn(long expiresIn) {
        this.expiresIn = expiresIn;
    }

    public UserResponse getUser() {
        return user;
    }

    public void setUser(UserResponse user) {
        this.user = user;
    }
}
