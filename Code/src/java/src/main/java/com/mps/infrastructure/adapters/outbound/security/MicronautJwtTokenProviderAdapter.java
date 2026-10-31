package com.mps.infrastructure.adapters.outbound.security;

import com.mps.domain.model.AuthToken;
import com.mps.domain.model.User;
import com.mps.domain.ports.outbound.TokenProviderPort;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.token.generator.AccessTokenConfiguration;
import io.micronaut.security.token.generator.TokenGenerator;
import jakarta.inject.Singleton;

import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Adaptador de seguridad que implementa TokenProviderPort emitiendo JWT firmados (HS256) con micronaut-security-jwt.
 * El 'sub' del token es el UUID opaco del usuario (RNF-23); el correo viaja como claim adicional.
 */
@Singleton
public class MicronautJwtTokenProviderAdapter implements TokenProviderPort {

    static final String TOKEN_TYPE = "Bearer";
    static final String ROLE_USER = "ROLE_USER";
    public static final String EMAIL_CLAIM = "email";

    private final TokenGenerator tokenGenerator;
    private final AccessTokenConfiguration accessTokenConfiguration;

    public MicronautJwtTokenProviderAdapter(TokenGenerator tokenGenerator, AccessTokenConfiguration accessTokenConfiguration) {
        this.tokenGenerator = Objects.requireNonNull(tokenGenerator, "TokenGenerator cannot be null");
        this.accessTokenConfiguration = Objects.requireNonNull(accessTokenConfiguration, "AccessTokenConfiguration cannot be null");
    }

    @Override
    public AuthToken issueToken(User user) {
        Objects.requireNonNull(user, "User cannot be null");

        Authentication authentication = Authentication.build(
                user.getId().toString(),
                List.of(ROLE_USER),
                Map.of(EMAIL_CLAIM, user.getEmail())
        );

        Integer expiration = accessTokenConfiguration.getExpiration();
        String accessToken = tokenGenerator.generateToken(authentication, expiration)
                .orElseThrow(() -> new IllegalStateException("Unable to generate JWT access token"));

        return new AuthToken(accessToken, TOKEN_TYPE, expiration);
    }
}
