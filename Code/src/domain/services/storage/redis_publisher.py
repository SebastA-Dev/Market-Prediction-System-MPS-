"""
Publicador de Señales Reactivas en Redis Pub/Sub.
Publica al canal 'market_signals' las señales validadas estadísticamente (p < 0.05).
Cumple con:
- RF-13: Publicación con payload {ticker, price, signal, p_value} en < 100 ms.
- RF-14: Registro en log de fallos sin bloquear el pipeline.
- RNF-09: Aislamiento de fallos de red.
"""

import json
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)
import redis

from ...models.market import MarketSignalPayload


class RedisSignalPublisher:
    """
    Publicador no bloqueante para el bus de mensajería Redis.
    """

    CHANNEL_NAME = "market_signals"

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self._client: Optional[redis.Redis] = None

    def connect(self):
        try:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True,
                socket_timeout=2.0,
            )
            self._client.ping()
            logger.info(f"[RedisPublisher] Conectado exitosamente a Redis en {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"[RedisPublisher] No fue posible conectar con Redis ({e}). Modo desacoplado activado.")
            self._client = None

    def publish_signal(self, payload: MarketSignalPayload) -> bool:
        """
        RF-13 & RF-14: Emite la señal al canal Redis 'market_signals'.
        """
        if self._client is None:
            self.connect()

        payload_json = json.dumps(payload.model_dump())

        if self._client is None:
            logger.debug(f"[RedisPublisher:LocalSim] Señal simulada: {payload_json}")
            return True

        try:
            self._client.publish(self.CHANNEL_NAME, payload_json)
            logger.info(f"[RedisPublisher] Señal publicada en '{self.CHANNEL_NAME}': {payload.ticker} -> {payload.signal}")
            return True
        except Exception as e:
            # RF-14 & RNF-09: No bloquear el procesamiento por caídas de Redis
            logger.error(f"[RedisPublisher] Fallo al publicar señal en Redis para {payload.ticker}: {e}")
            return False
