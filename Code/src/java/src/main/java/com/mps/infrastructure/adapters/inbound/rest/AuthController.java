package com.mps.infrastructure.adapters.inbound.rest;

import com.mps.domain.exception.InvalidCredentialsException;
import com.mps.domain.exception.TooManyLoginAttemptsException;
import com.mps.domain.model.AuthenticatedSession;
import com.mps.domain.model.User;
import com.mps.domain.ports.inbound.LoginUserCommand;
import com.mps.domain.ports.inbound.LoginUserUseCase;
import com.mps.infrastructure.adapters.inbound.rest.dto.CurrentUserResponse;
import com.mps.infrastructure.adapters.inbound.rest.dto.ErrorResponse;
import com.mps.infrastructure.adapters.inbound.rest.dto.LoginRequest;
import com.mps.infrastructure.adapters.inbound.rest.dto.LoginResponse;
import com.mps.infrastructure.adapters.inbound.rest.dto.UserResponse;
import com.mps.infrastructure.adapters.outbound.security.MicronautJwtTokenProviderAdapter;
import io.micronaut.http.HttpHeaders;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Error;
import io.micronaut.http.annotation.Get;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;

import java.util.List;
import java.util.Objects;

/**
 * Adaptador primario (Inbound REST Controller) para la autenticación de usuarios con JWT.
 * El token emitido en /login debe enviarse como 'Authorization: Bearer <token>' en los endpoints protegidos.
 */
@Controller("/api/v1/auth")
@Tag(name = "Autenticación", description = "Inicio de sesión y validación de tokens JWT")
public class AuthController {

    private final LoginUserUseCase loginUserUseCase;

    public AuthController(LoginUserUseCase loginUserUseCase) {
        this.loginUserUseCase = Objects.requireNonNull(loginUserUseCase, "LoginUserUseCase cannot be null");
    }

    @Post("/login")
    @Secured(SecurityRule.IS_ANONYMOUS)
    @Operation(
            summary = "Iniciar sesión",
            description = "Verifica el correo y la contraseña contra el hash PBKDF2 almacenado y emite un JWT firmado."
    )
    @ApiResponse(
            responseCode = "200",
            description = "Autenticación exitosa",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))
    )
    @ApiResponse(
            responseCode = "400",
            description = "Datos de inicio de sesión inválidos o incompletos",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
    @ApiResponse(
            responseCode = "401",
            description = "Correo o contraseña incorrectos",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
    @ApiResponse(
            responseCode = "429",
            description = "Cuenta bloqueada temporalmente por exceso de intentos fallidos",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
    public HttpResponse<LoginResponse> login(@Valid @NotNull @Body LoginRequest request) {
        LoginUserCommand command = new LoginUserCommand(request.getEmail(), request.getPassword());
        AuthenticatedSession session = loginUserUseCase.login(command);

        User user = session.user();
        LoginResponse response = new LoginResponse(
                session.token().accessToken(),
                session.token().tokenType(),
                session.token().expiresInSeconds(),
                new UserResponse(user.getId(), user.getEmail(), user.getCreatedAt())
        );

        return HttpResponse.ok(response)
                .header(HttpHeaders.CACHE_CONTROL, "no-store");
    }

    @Get("/me")
    @Secured(SecurityRule.IS_AUTHENTICATED)
    @SecurityRequirement(name = "BearerAuth")
    @Operation(
            summary = "Usuario autenticado",
            description = "Devuelve la identidad contenida en el JWT enviado en la cabecera Authorization."
    )
    @ApiResponse(
            responseCode = "200",
            description = "Token válido",
            content = @Content(schema = @Schema(implementation = CurrentUserResponse.class))
    )
    @ApiResponse(responseCode = "401", description = "Token ausente, inválido o expirado")
    public CurrentUserResponse me(Authentication authentication) {
        Object email = authentication.getAttributes().get(MicronautJwtTokenProviderAdapter.EMAIL_CLAIM);
        return new CurrentUserResponse(authentication.getName(), email == null ? null : email.toString());
    }

    @Error(exception = InvalidCredentialsException.class)
    public HttpResponse<ErrorResponse> onInvalidCredentials(InvalidCredentialsException ex) {
        ErrorResponse error = new ErrorResponse(
                HttpStatus.UNAUTHORIZED.getCode(),
                HttpStatus.UNAUTHORIZED.getReason(),
                ex.getMessage()
        );
        return HttpResponse.<ErrorResponse>status(HttpStatus.UNAUTHORIZED).body(error);
    }

    @Error(exception = TooManyLoginAttemptsException.class)
    public HttpResponse<ErrorResponse> onTooManyAttempts(TooManyLoginAttemptsException ex) {
        ErrorResponse error = new ErrorResponse(
                HttpStatus.TOO_MANY_REQUESTS.getCode(),
                HttpStatus.TOO_MANY_REQUESTS.getReason(),
                ex.getMessage()
        );
        return HttpResponse.<ErrorResponse>status(HttpStatus.TOO_MANY_REQUESTS)
                .header(HttpHeaders.RETRY_AFTER, String.valueOf(ex.getRetryAfterSeconds()))
                .body(error);
    }

    @Error(exception = ConstraintViolationException.class)
    public HttpResponse<ErrorResponse> onConstraintViolation(ConstraintViolationException ex) {
        List<String> details = ex.getConstraintViolations().stream()
                .map(ConstraintViolation::getMessage)
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
