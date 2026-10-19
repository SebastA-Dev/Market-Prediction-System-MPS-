package com.mps.domain.ports.outbound;

/**
 * Puerto secundario para el cifrado y validación de contraseñas con salting (RNF-26).
 */
public interface PasswordEncoderPort {

    String encode(String rawPassword);

    boolean matches(String rawPassword, String encodedPassword);
}
