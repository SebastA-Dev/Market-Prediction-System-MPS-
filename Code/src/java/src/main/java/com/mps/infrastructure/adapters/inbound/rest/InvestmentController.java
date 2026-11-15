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
import io.micronaut.http.annotation.Delete;
import io.micronaut.http.annotation.Get;
import io.micronaut.http.annotation.PathVariable;
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
import java.util.Locale;
import java.util.Objects;
import java.util.UUID;
import java.util.regex.Pattern;

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

    /** Mismo formato que asset.ticker (VARCHAR(20)): letras, números y . - ^ = */
    private static final Pattern TICKER_PATTERN = Pattern.compile("^[A-Z0-9.\\-^=]{1,20}$");

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
        UUID userId = resolveUserId(authentication);
        if (userId == null) {
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

    @Delete("/{ticker}")
    @Operation(summary = "Eliminar inversión del portafolio",
            description = "Deja de seguir un activo: borra de user_configuration la fila del usuario del JWT "
                    + "para ese ticker. El activo sigue existiendo en 'asset' y no afecta a otros usuarios.")
    @ApiResponse(responseCode = "200", description = "Activo eliminado del portafolio")
    @ApiResponse(responseCode = "400", description = "Ticker con formato inválido")
    @ApiResponse(responseCode = "401", description = "Token ausente, inválido o expirado")
    @ApiResponse(responseCode = "404", description = "El usuario no existe o no tiene ese activo en su portafolio")
    public HttpResponse<?> deleteFromPortfolio(Authentication authentication, @PathVariable String ticker) {
        // 1-2. Sesión activa: lo valida @Secured(IS_AUTHENTICATED) antes de llegar aquí (401).
        // 3. Validar solicitud: usuario del token y formato del ticker.
        UUID userId = resolveUserId(authentication);
        if (userId == null) {
            return error(HttpStatus.UNAUTHORIZED, "El token no contiene un identificador de usuario válido");
        }
        if (userRepository.findById(userId).isEmpty()) {
            return error(HttpStatus.NOT_FOUND, "El usuario del token no existe");
        }
        String normalizedTicker = ticker == null ? "" : ticker.trim().toUpperCase(Locale.ROOT);
        if (!TICKER_PATTERN.matcher(normalizedTicker).matches()) {
            return error(HttpStatus.BAD_REQUEST, "El ticker no tiene un formato válido");
        }

        // 4. Eliminar solo la fila de ESTE usuario (nunca la de otro) mediante el ORM.
        long deleted = configurationRepository.deleteByUserIdAndAssetTicker(userId, normalizedTicker);
        if (deleted == 0) {
            return error(HttpStatus.NOT_FOUND, "El activo " + normalizedTicker + " no está en tu portafolio");
        }
        return HttpResponse.ok(new DeleteResponse(normalizedTicker, "Activo eliminado del portafolio"));
    }

    private static UUID resolveUserId(Authentication authentication) {
        try {
            return UUID.fromString(authentication.getName());
        } catch (IllegalArgumentException | NullPointerException e) {
            return null;
        }
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
    public record DeleteResponse(String ticker, String message) {
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
