package com.mps.infrastructure.adapters.inbound.rest;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.mps.domain.ports.outbound.UserRepositoryPort;
import com.mps.infrastructure.adapters.inbound.rest.dto.ErrorResponse;
import com.mps.infrastructure.adapters.outbound.persistence.entity.UserConfigurationEntity;
import com.mps.infrastructure.adapters.outbound.persistence.repository.UserConfigurationRepository;
import io.micronaut.core.annotation.Introspected;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.serde.annotation.Serdeable;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * Endpoint de inversiones del usuario autenticado.
 * Flujo: ¿hay token? -> ¿la sesión (JWT) sigue activa? -> validar solicitud -> traer datos.
 * Los dos primeros pasos los hace Micronaut Security con @Secured(IS_AUTHENTICATED): sin token
 * válido o con el token vencido responde 401 antes de entrar al método.
 */
@Controller("/api/v1/portfolio")
@Secured(SecurityRule.IS_AUTHENTICATED)
@SecurityRequirement(name = "BearerAuth")
@Tag(name = "Inversiones", description = "Activos que sigue el usuario autenticado")
public class InvestmentController {

    private final UserRepositoryPort userRepository;
    private final UserConfigurationRepository configurationRepository;

    public InvestmentController(UserRepositoryPort userRepository,
                                UserConfigurationRepository configurationRepository) {
        this.userRepository = Objects.requireNonNull(userRepository, "UserRepositoryPort cannot be null");
        this.configurationRepository = Objects.requireNonNull(configurationRepository, "UserConfigurationRepository cannot be null");
    }

    @Get
    @Operation(summary = "Inversiones del usuario",
            description = "Devuelve los activos que sigue el usuario dueño del JWT (user_configuration + asset).")
    @ApiResponse(responseCode = "200", description = "Lista de activos (puede estar vacía)")
    @ApiResponse(responseCode = "401", description = "Token ausente, inválido o expirado")
    @ApiResponse(responseCode = "404", description = "El usuario del token ya no existe")
    public HttpResponse<?> getPortfolio(Authentication authentication) {
        // Validar solicitud: el 'sub' del JWT debe ser un UUID de un usuario existente.
        UUID userId;
        try {
            userId = UUID.fromString(authentication.getName());
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.UNAUTHORIZED, "El token no contiene un identificador de usuario válido");
        }
        if (userRepository.findById(userId).isEmpty()) {
            return error(HttpStatus.NOT_FOUND, "El usuario del token no existe");
        }

        // Traer los datos del usuario (ORM).
        List<PortfolioItem> items = configurationRepository.findByUserIdOrderByCreatedAtAsc(userId).stream()
                .map(PortfolioItem::from)
                .toList();

        return HttpResponse.ok(new PortfolioResponse(userId, items.size(), items));
    }

    private static HttpResponse<ErrorResponse> error(HttpStatus status, String message) {
        return HttpResponse.<ErrorResponse>status(status)
                .body(new ErrorResponse(status.getCode(), status.getReason(), message));
    }

    @Serdeable
    @Introspected
    @JsonInclude(JsonInclude.Include.ALWAYS)
    public record PortfolioResponse(UUID userId, int total, List<PortfolioItem> assets) {
    }

    @Serdeable
    @Introspected
    public record PortfolioItem(String ticker, String name, String sector, boolean active,
                                boolean alertsEnabled, Instant followingSince) {
        static PortfolioItem from(UserConfigurationEntity config) {
            var asset = config.getAsset();
            return new PortfolioItem(asset.getTicker(), asset.getName(), asset.getSector(), asset.isActive(),
                    config.isAlertsEnabled(), config.getCreatedAt());
        }
    }
}
