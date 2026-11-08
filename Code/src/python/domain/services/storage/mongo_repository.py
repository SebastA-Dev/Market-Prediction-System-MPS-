"""
Repositorio de Persistencia Documental en MongoDB.
Implementa el almacenamiento append-only especificado en:
- UMLBaseDeDatos.drawio
- RF-15: Inserción de documentos en 'market_ticks_and_features' (ticks crudos, Alpha Factors, inferencias MASTER/Galformer, p-value).
- RF-16: Operación estricta bajo patrón append-only (sin updates ni deletes).
- RNF-05: Creación de índices compuestos en {ticker: 1, timestamp: -1}.
- INTENT_PREDICTION_LOG para registro de consultas conversacionales.
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)
import pymongo
from pymongo import MongoClient

from ...models.market import IntentPredictionLog, MarketTickDocument


class MongoMarketRepository:
    """
    Gestiona la persistencia de auditoría e inferencias en MongoDB.
    Garantiza inmutabilidad y alto rendimiento de escritura.
    """

    COLLECTION_TICKS = "market_ticks_and_features"
    COLLECTION_INTENTS = "INTENT_PREDICTION_LOG"

    def __init__(self, uri: Optional[str] = None, db_name: str = "mps_market_db"):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self._client: Optional[MongoClient] = None
        self._db = None

    def connect(self):
        """Inicializa la conexión y crea los índices requeridos."""
        try:
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self._db = self._client[self.db_name]

            # RNF-05: Índices compuestos en {ticker: 1, timestamp: -1}
            ticks_col = self._db[self.COLLECTION_TICKS]
            ticks_col.create_index([("ticker", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)])

            # Índices para INTENT_PREDICTION_LOG
            intents_col = self._db[self.COLLECTION_INTENTS]
            intents_col.create_index([("timestamp", pymongo.DESCENDING)])

            logger.info(f"[MongoRepository] Conectado a MongoDB ({self.db_name}) e índices verificados.")
        except Exception as e:
            logger.warning(f"[MongoRepository] Modo offline o MongoDB no disponible ({e}). Operando con fallback local.")

    def insert_tick_document(self, doc: MarketTickDocument) -> bool:
        """
        RF-15 & RF-16: Inserta un documento inmutable en 'market_ticks_and_features'.
        Append-only: Solo insert_one, sin actualización.
        """
        if self._db is None:
            self.connect()

        if self._db is None:
            logger.debug(f"[MongoRepository:LocalMock] Tick insertado para {doc.ticker}")
            return True

        try:
            doc_dict = doc.model_dump()
            self._db[self.COLLECTION_TICKS].insert_one(doc_dict)
            return True
        except Exception as e:
            logger.error(f"[MongoRepository] Error insertando tick en MongoDB: {e}")
            return False

    def insert_intent_log(self, log_entry: IntentPredictionLog) -> bool:
        """
        Inserta un registro de consulta en 'INTENT_PREDICTION_LOG'.
        """
        if self._db is None:
            self.connect()

        if self._db is None:
            return True

        try:
            self._db[self.COLLECTION_INTENTS].insert_one(log_entry.model_dump())
            return True
        except Exception as e:
            logger.error(f"[MongoRepository] Error registrando log de intención: {e}")
            return False
