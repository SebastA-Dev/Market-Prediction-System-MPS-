package com.mps.domain.ports.outbound;

import com.mps.domain.model.AuthToken;
import com.mps.domain.model.User;

/**
 * Puerto secundario para la emisión de tokens de acceso firmados (JWT) para un usuario autenticado.
 */
public interface TokenProviderPort {

    AuthToken issueToken(User user);
}
