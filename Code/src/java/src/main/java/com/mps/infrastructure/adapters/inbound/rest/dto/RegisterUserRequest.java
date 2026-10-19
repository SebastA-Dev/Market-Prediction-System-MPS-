package com.mps.infrastructure.adapters.inbound.rest.dto;

import io.micronaut.core.annotation.Introspected;
import io.micronaut.serde.annotation.Serdeable;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * DTO para la petición de registro de usuario (UC-09a).
 */
@Serdeable
@Introspected
@Schema(description = "Payload para el registro de un nuevo usuario")
public class RegisterUserRequest {

    @NotBlank(message = "El correo electrónico es obligatorio")
    @Email(message = "El formato del correo electrónico es inválido")
    @Size(max = 255, message = "El correo no puede exceder los 255 caracteres")
    @Schema(description = "Correo electrónico del usuario", example = "usuario@mps.com")
    private String email;

    @NotBlank(message = "La contraseña es obligatoria")
    @Size(min = 8, max = 128, message = "La contraseña debe contener al menos 8 caracteres")
    @Schema(description = "Contraseña en texto plano para el registro", example = "SecretPass123*")
    private String password;

    public RegisterUserRequest() {
    }

    public RegisterUserRequest(String email, String password) {
        this.email = email;
        this.password = password;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
