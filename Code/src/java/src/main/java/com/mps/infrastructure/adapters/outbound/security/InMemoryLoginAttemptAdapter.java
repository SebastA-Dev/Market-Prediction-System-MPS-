package com.mps.infrastructure.adapters.outbound.security;

import com.mps.domain.ports.outbound.LoginAttemptPort;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Singleton;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Adaptador en memoria que limita los intentos fallidos de inicio de sesión por correo.
 * Tras N fallos consecutivos la cuenta queda bloqueada durante una ventana configurable.
 * Para un despliegue con varias réplicas debe sustituirse por un adaptador respaldado en Redis.
 */
@Singleton
public class InMemoryLoginAttemptAdapter implements LoginAttemptPort {

    private record Attempts(int failures, Instant lockedUntil) {
    }

    private final Map<String, Attempts> attemptsByEmail = new ConcurrentHashMap<>();
    private final int maxFailures;
    private final Duration lockDuration;
    private final Clock clock;

    public InMemoryLoginAttemptAdapter(
            @Value("${mps.security.login.max-failed-attempts:5}") int maxFailures,
            @Value("${mps.security.login.lock-duration:15m}") Duration lockDuration
    ) {
        this(maxFailures, lockDuration, Clock.systemUTC());
    }

    InMemoryLoginAttemptAdapter(int maxFailures, Duration lockDuration, Clock clock) {
        this.maxFailures = maxFailures;
        this.lockDuration = lockDuration;
        this.clock = clock;
    }

    @Override
    public long remainingLockSeconds(String email) {
        Attempts attempts = attemptsByEmail.get(email);
        if (attempts == null || attempts.lockedUntil() == null) {
            return 0;
        }
        long remaining = Duration.between(clock.instant(), attempts.lockedUntil()).toSeconds();
        if (remaining <= 0) {
            attemptsByEmail.remove(email);
            return 0;
        }
        return remaining;
    }

    @Override
    public void recordFailure(String email) {
        attemptsByEmail.compute(email, (key, current) -> {
            Instant now = clock.instant();
            boolean expiredLock = current != null && current.lockedUntil() != null && !now.isBefore(current.lockedUntil());
            int failures = (current == null || expiredLock ? 0 : current.failures()) + 1;
            Instant lockedUntil = failures >= maxFailures ? now.plus(lockDuration) : null;
            return new Attempts(failures, lockedUntil);
        });
    }

    @Override
    public void reset(String email) {
        attemptsByEmail.remove(email);
    }
}
