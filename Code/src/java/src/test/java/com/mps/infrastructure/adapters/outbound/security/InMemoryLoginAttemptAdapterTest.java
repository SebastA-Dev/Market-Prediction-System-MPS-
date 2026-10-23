package com.mps.infrastructure.adapters.outbound.security;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Pruebas Unitarias: InMemoryLoginAttemptAdapter")
class InMemoryLoginAttemptAdapterTest {

    private static final Instant NOW = Instant.parse("2026-10-23T12:00:00Z");

    @Test
    @DisplayName("Debe bloquear al alcanzar el máximo de fallos y desbloquear al vencer la ventana")
    void shouldLockAndUnlock() {
        MutableClock clock = new MutableClock(NOW);
        InMemoryLoginAttemptAdapter adapter = new InMemoryLoginAttemptAdapter(2, Duration.ofMinutes(15), clock);

        adapter.recordFailure("a@mps.com");
        assertEquals(0, adapter.remainingLockSeconds("a@mps.com"));

        adapter.recordFailure("a@mps.com");
        assertEquals(900, adapter.remainingLockSeconds("a@mps.com"));

        clock.now = NOW.plusSeconds(901);
        assertEquals(0, adapter.remainingLockSeconds("a@mps.com"));

        // Tras el desbloqueo el contador empieza de cero
        adapter.recordFailure("a@mps.com");
        assertEquals(0, adapter.remainingLockSeconds("a@mps.com"));
    }

    @Test
    @DisplayName("Debe olvidar los fallos tras reset")
    void shouldResetFailures() {
        InMemoryLoginAttemptAdapter adapter = new InMemoryLoginAttemptAdapter(2, Duration.ofMinutes(15), Clock.fixed(NOW, ZoneOffset.UTC));

        adapter.recordFailure("a@mps.com");
        adapter.reset("a@mps.com");
        adapter.recordFailure("a@mps.com");

        assertEquals(0, adapter.remainingLockSeconds("a@mps.com"));
    }

    static class MutableClock extends Clock {
        Instant now;

        MutableClock(Instant now) {
            this.now = now;
        }

        @Override
        public ZoneOffset getZone() {
            return ZoneOffset.UTC;
        }

        @Override
        public Clock withZone(java.time.ZoneId zone) {
            return this;
        }

        @Override
        public Instant instant() {
            return now;
        }
    }
}
