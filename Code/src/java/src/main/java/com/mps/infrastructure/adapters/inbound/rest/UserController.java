package com.mps.infrastructure.adapters.inbound.rest;

import com.mps.domain.model.User;
import com.mps.domain.ports.inbound.RegisterUserCommand;
import com.mps.domain.ports.inbound.RegisterUserUseCase;
import com.mps.infrastructure.adapters.inbound.rest.dto.ErrorResponse;
import com.mps.infrastructure.adapters.inbound.rest.dto.RegisterUserRequest;
import com.mps.infrastructure.adapters.inbound.rest.dto.UserResponse;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;

import java.util.Objects;

/**
 * Adaptador primario (Inbound REST Controller) para la gestión y registro de usuarios.
 * Expone la API RESTful bajo el estándar especificado en los diagramas de secuencia (UC-09a).
 */
@Controller("/api/v1/users")
@Secured(SecurityRule.IS_ANONYMOUS)
@Tag(name = "Usuarios", description = "Endpoints de gestión de identidad y registro de usuarios")
public class UserController {

    private final RegisterUserUseCase registerUserUseCase;

    public UserController(RegisterUserUseCase registerUserUseCase) {
        this.registerUserUseCase = Objects.requireNonNull(registerUserUseCase, "RegisterUserUseCase cannot be null");
    }

    @Post
    @Status(HttpStatus.CREATED)
    @Operation(
            summary = "Registrar nuevo usuario",
            description = "Valida el correo, genera un identificador criptográfico único (UUID v4) y cifra la contraseña antes de persistir."
    )
    @ApiResponse(
            responseCode = "201",
            description = "Usuario registrado exitosamente",
            content = @Content(schema = @Schema(implementation = UserResponse.class))
    )
    @ApiResponse(
            responseCode = "400",
            description = "Datos de registro inválidos o incompletos",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
    @ApiResponse(
            responseCode = "409",
            description = "Conflicto: El correo electrónico ya se encuentra registrado",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
    public HttpResponse<UserResponse> register(@Valid @NotNull @Body RegisterUserRequest request) {
        RegisterUserCommand command = new RegisterUserCommand(request.getEmail(), request.getPassword());
        User user = registerUserUseCase.register(command);

        UserResponse response = new UserResponse(
                user.getId(),
                user.getEmail(),
                user.getCreatedAt()
        );

        return HttpResponse.created(response);
    }

    @io.micronaut.http.annotation.Error(exception = com.mps.domain.exception.UserAlreadyExistsException.class)
    public HttpResponse<ErrorResponse> onUserAlreadyExists(com.mps.domain.exception.UserAlreadyExistsException ex) {
        ErrorResponse error = new ErrorResponse(
                HttpStatus.CONFLICT.getCode(),
                HttpStatus.CONFLICT.getReason(),
                ex.getMessage()
        );
        return HttpResponse.status(HttpStatus.CONFLICT).body(error);
    }

    @io.micronaut.http.annotation.Error(exception = com.mps.domain.exception.InvalidUserDataException.class)
    public HttpResponse<ErrorResponse> onInvalidUserData(com.mps.domain.exception.InvalidUserDataException ex) {
        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.getCode(),
                HttpStatus.BAD_REQUEST.getReason(),
                ex.getMessage()
        );
        return HttpResponse.badRequest(error);
    }

    @io.micronaut.http.annotation.Error(exception = jakarta.validation.ConstraintViolationException.class)
    public HttpResponse<ErrorResponse> onConstraintViolation(jakarta.validation.ConstraintViolationException ex) {
        java.util.List<String> details = ex.getConstraintViolations().stream()
                .map(jakarta.validation.ConstraintViolation::getMessage)
                .toList();

        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.getCode(),
                HttpStatus.BAD_REQUEST.getReason(),
                "Validation failed for request payload",
                details
        );
        return HttpResponse.badRequest(error);
    }
}
