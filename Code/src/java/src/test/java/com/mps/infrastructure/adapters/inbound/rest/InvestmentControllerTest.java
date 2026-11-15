package com.mps.infrastructure.adapters.inbound.rest;

import com.mps.infrastructure.adapters.inbound.rest.dto.LoginRequest;
import com.mps.infrastructure.adapters.inbound.rest.dto.LoginResponse;
import com.mps.infrastructure.adapters.inbound.rest.dto.RegisterUserRequest;
import com.mps.infrastructure.adapters.inbound.rest.dto.UserResponse;
import com.mps.infrastructure.adapters.outbound.persistence.entity.AssetEntity;
import com.mps.infrastructure.adapters.outbound.persistence.entity.UserConfigurationEntity;
import com.mps.infrastructure.adapters.outbound.persistence.repository.UserConfigurationRepository;
import io.micronaut.data.annotation.Repository;
import io.micronaut.data.repository.CrudRepository;
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

import java.time.Instant;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@MicronautTest(transactional = false)
@DisplayName("Pruebas de Integración HTTP: InvestmentController (/api/v1/portfolio)")
class InvestmentControllerTest {

    private static final String PASSWORD = "StrongPassword123*";

    @Repository
    interface TestAssetRepository extends CrudRepository<AssetEntity, String> {
    }

    @Inject
    @Client("/")
    HttpClient client;

    @Inject
    TestAssetRepository assetRepository;

    @Inject
    UserConfigurationRepository configurationRepository;

    private LoginResponse registerAndLogin() {
        String email = "portfolio_" + System.nanoTime() + "@mps.com";
        client.toBlocking().exchange(HttpRequest.POST("/api/v1/users", new RegisterUserRequest(email, PASSWORD)),
                UserResponse.class);
        return client.toBlocking().retrieve(HttpRequest.POST("/api/v1/auth/login", new LoginRequest(email, PASSWORD)),
                LoginResponse.class);
    }

    @Test
    @DisplayName("GET /api/v1/portfolio sin token debe responder 401")
    void shouldRejectWithoutToken() {
        HttpClientResponseException ex = assertThrows(HttpClientResponseException.class,
                () -> client.toBlocking().exchange(HttpRequest.GET("/api/v1/portfolio")));
        assertEquals(HttpStatus.UNAUTHORIZED, ex.getStatus());
    }

    @Test
    @DisplayName("GET /api/v1/portfolio con token inválido debe responder 401")
    void shouldRejectInvalidToken() {
        HttpClientResponseException ex = assertThrows(HttpClientResponseException.class,
                () -> client.toBlocking().exchange(HttpRequest.GET("/api/v1/portfolio").bearerAuth("token.falso.123")));
        assertEquals(HttpStatus.UNAUTHORIZED, ex.getStatus());
    }

    @Test
    @DisplayName("GET /api/v1/portfolio debe devolver solo los activos del usuario autenticado")
    void shouldReturnUserAssets() {
        LoginResponse session = registerAndLogin();
        UUID userId = session.getUser().getId();
        LoginResponse other = registerAndLogin();

        String ticker = "T" + (System.nanoTime() % 1_000_000);
        AssetEntity asset = assetRepository.save(new AssetEntity(ticker, "Apple Inc.", "Tecnologia", true));
        configurationRepository.save(new UserConfigurationEntity(UUID.randomUUID(), userId, asset, true, Instant.now()));
        configurationRepository.save(new UserConfigurationEntity(UUID.randomUUID(), other.getUser().getId(), asset, false, Instant.now()));

        HttpResponse<InvestmentController.PortfolioResponse> response = client.toBlocking().exchange(
                HttpRequest.GET("/api/v1/portfolio").bearerAuth(session.getAccessToken()),
                InvestmentController.PortfolioResponse.class);

        assertEquals(HttpStatus.OK, response.status());
        InvestmentController.PortfolioResponse body = response.body();
        assertNotNull(body);
        assertEquals(userId, body.userId());
        assertEquals(1, body.total());
        InvestmentController.PortfolioItem item = body.assets().get(0);
        assertEquals(ticker, item.ticker());
        assertEquals("Apple Inc.", item.name());
        assertEquals("Tecnologia", item.sector());
        assertTrue(item.alertsEnabled());
    }

    @Test
    @DisplayName("GET /api/v1/portfolio de un usuario sin activos devuelve lista vacía")
    void shouldReturnEmptyList() {
        LoginResponse session = registerAndLogin();
        InvestmentController.PortfolioResponse body = client.toBlocking().retrieve(
                HttpRequest.GET("/api/v1/portfolio").bearerAuth(session.getAccessToken()),
                InvestmentController.PortfolioResponse.class);
        assertEquals(0, body.total());
        assertTrue(body.assets().isEmpty());
    }

    private String createAsset() {
        String ticker = "D" + (System.nanoTime() % 1_000_000);
        assetRepository.save(new AssetEntity(ticker, "Empresa " + ticker, "Tecnologia", true));
        return ticker;
    }

    private void follow(UUID userId, String ticker) {
        AssetEntity asset = assetRepository.findById(ticker).orElseThrow();
        configurationRepository.save(new UserConfigurationEntity(UUID.randomUUID(), userId, asset, true, Instant.now()));
    }

    private InvestmentController.PortfolioResponse portfolio(String token) {
        return client.toBlocking().retrieve(HttpRequest.GET("/api/v1/portfolio").bearerAuth(token),
                InvestmentController.PortfolioResponse.class);
    }

    private HttpStatus deleteExpectingError(String path, String token) {
        HttpRequest<?> request = HttpRequest.DELETE(path);
        if (token != null) {
            request = HttpRequest.DELETE(path).bearerAuth(token);
        }
        HttpRequest<?> finalRequest = request;
        HttpClientResponseException ex = assertThrows(HttpClientResponseException.class,
                () -> client.toBlocking().exchange(finalRequest));
        return ex.getStatus();
    }

    @Test
    @DisplayName("DELETE /api/v1/portfolio/{ticker} elimina el activo solo del portafolio del usuario")
    void shouldDeleteAssetFromOwnPortfolioOnly() {
        LoginResponse session = registerAndLogin();
        LoginResponse other = registerAndLogin();
        String keep = createAsset();
        String remove = createAsset();
        follow(session.getUser().getId(), keep);
        follow(session.getUser().getId(), remove);
        follow(other.getUser().getId(), remove);

        HttpResponse<InvestmentController.DeleteResponse> response = client.toBlocking().exchange(
                HttpRequest.DELETE("/api/v1/portfolio/" + remove.toLowerCase()).bearerAuth(session.getAccessToken()),
                InvestmentController.DeleteResponse.class);
        assertEquals(HttpStatus.OK, response.status());
        assertEquals(remove, response.body().ticker());

        InvestmentController.PortfolioResponse mine = portfolio(session.getAccessToken());
        assertEquals(1, mine.total());
        assertEquals(keep, mine.assets().get(0).ticker());

        // El otro usuario conserva su activo y el activo sigue existiendo en 'asset'.
        InvestmentController.PortfolioResponse theirs = portfolio(other.getAccessToken());
        assertEquals(1, theirs.total());
        assertEquals(remove, theirs.assets().get(0).ticker());
        assertTrue(assetRepository.existsById(remove));
    }

    @Test
    @DisplayName("DELETE de un activo que el usuario no sigue debe responder 404")
    void shouldReturn404WhenAssetNotInPortfolio() {
        LoginResponse session = registerAndLogin();
        String ticker = createAsset();
        assertEquals(HttpStatus.NOT_FOUND,
                deleteExpectingError("/api/v1/portfolio/" + ticker, session.getAccessToken()));
    }

    @Test
    @DisplayName("DELETE dos veces del mismo activo: la segunda responde 404")
    void shouldReturn404OnSecondDelete() {
        LoginResponse session = registerAndLogin();
        String ticker = createAsset();
        follow(session.getUser().getId(), ticker);
        client.toBlocking().exchange(HttpRequest.DELETE("/api/v1/portfolio/" + ticker).bearerAuth(session.getAccessToken()));
        assertEquals(HttpStatus.NOT_FOUND,
                deleteExpectingError("/api/v1/portfolio/" + ticker, session.getAccessToken()));
    }

    @Test
    @DisplayName("DELETE con ticker inválido debe responder 400")
    void shouldReturn400ForInvalidTicker() {
        LoginResponse session = registerAndLogin();
        assertEquals(HttpStatus.BAD_REQUEST,
                deleteExpectingError("/api/v1/portfolio/TICKER_DEMASIADO_LARGO_123", session.getAccessToken()));
        assertEquals(HttpStatus.BAD_REQUEST,
                deleteExpectingError("/api/v1/portfolio/ABC*D", session.getAccessToken()));
    }

    @Test
    @DisplayName("DELETE sin token debe responder 401")
    void shouldRejectDeleteWithoutToken() {
        assertEquals(HttpStatus.UNAUTHORIZED, deleteExpectingError("/api/v1/portfolio/AAPL", null));
    }
}
