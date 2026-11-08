package com.mps.infrastructure.adapters.outbound.security;

import com.mps.domain.ports.outbound.PasswordEncoderPort;
import jakarta.inject.Singleton;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.util.Base64;

/**
 * Adaptador de seguridad que implementa PasswordEncoderPort mediante PBKDF2 con HMAC-SHA256 y Salt aleatorio.
 * Cumple con RNF-26 (Protección y cifrado en reposo con salting).
 */
@Singleton
public class PBKDF2PasswordEncoderAdapter implements PasswordEncoderPort {

    private static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    private static final int ITERATIONS = 65536;
    private static final int KEY_LENGTH = 256;
    private static final int SALT_BYTES = 16;

    private final SecureRandom secureRandom = new SecureRandom();

    @Override
    public String encode(String rawPassword) {
        if (rawPassword == null) {
            throw new IllegalArgumentException("Raw password cannot be null");
        }

        byte[] salt = new byte[SALT_BYTES];
        secureRandom.nextBytes(salt);

        byte[] hash = pbkdf2(rawPassword.toCharArray(), salt, ITERATIONS, KEY_LENGTH);

        String saltBase64 = Base64.getEncoder().encodeToString(salt);
        String hashBase64 = Base64.getEncoder().encodeToString(hash);

        return "$pbkdf2-sha256$" + ITERATIONS + "$" + saltBase64 + "$" + hashBase64;
    }

    @Override
    public boolean matches(String rawPassword, String encodedPassword) {
        if (rawPassword == null || encodedPassword == null) {
            return false;
        }

        String[] parts = encodedPassword.split("\\$");
        if (parts.length != 5 || !parts[1].equals("pbkdf2-sha256")) {
            return false;
        }

        int iterations = Integer.parseInt(parts[2]);
        byte[] salt = Base64.getDecoder().decode(parts[3]);
        byte[] expectedHash = Base64.getDecoder().decode(parts[4]);

        byte[] computedHash = pbkdf2(rawPassword.toCharArray(), salt, iterations, expectedHash.length * 8);

        return MessageDigest.isEqual(expectedHash, computedHash);
    }

    private byte[] pbkdf2(char[] password, byte[] salt, int iterations, int keyLength) {
        try {
            PBEKeySpec spec = new PBEKeySpec(password, salt, iterations, keyLength);
            SecretKeyFactory skf = SecretKeyFactory.getInstance(ALGORITHM);
            return skf.generateSecret(spec).getEncoded();
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            throw new IllegalStateException("Cryptographic algorithm error while hashing password", e);
        }
    }
}
