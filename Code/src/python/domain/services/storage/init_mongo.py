"""
Script de Inicialización y Configuración de MongoDB para MPS.
Crea la base de datos 'mps_market_db', sus colecciones con validadores JSON Schema
y los índices compuestos optimizados según la especificación técnica en:
- UMLBaseDeDatos.drawio
- RF-15 & RF-16: Inmutabilidad y append-only en 'market_ticks_and_features'
- RNF-05: Índices compuestos {ticker: 1, timestamp: -1} para alto rendimiento de escritura
- INTENT_PREDICTION_LOG para registro de consultas conversacionales
"""

import os
import sys
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid, ConnectionFailure

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MongoInit")


def initialize_mongo(
    mongo_uri: str = "mongodb://localhost:27017",
    db_name: str = "mps_market_db",
) -> bool:
    """
    Inicializa colecciones, validadores e índices en MongoDB.
    """
    try:
        logger.info(f"Conectando a MongoDB en: {mongo_uri}...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=4000)
        # Forzar chequeo de conexión
        client.admin.command("ping")
        logger.info("Conexión con el servidor MongoDB establecida exitosamente.")
    except ConnectionFailure as e:
        logger.error(f"No se pudo conectar a MongoDB ({e}). Asegúrate de que el servicio esté corriendo.")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al conectar con MongoDB: {e}")
        return False

    db = client[db_name]

    # ==========================================================================
    # 1. Colección 'market_ticks_and_features' (Pipeline Analítico Streaming)
    # ==========================================================================
    ticks_col_name = "market_ticks_and_features"
    ticks_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["ticker", "timestamp", "raw_data", "statistical_validation"],
            "properties": {
                "ticker": {
                    "bsonType": "string",
                    "description": "Símbolo bursátil o criptoactivo (VARCHAR(20))",
                },
                "timestamp": {
                    "bsonType": "date",
                    "description": "Estampa temporal UTC del evento",
                },
                "raw_data": {
                    "bsonType": "object",
                    "required": ["price", "volume"],
                    "properties": {
                        "price": {"bsonType": "double", "description": "Precio observado"},
                        "volume": {"bsonType": "double", "description": "Volumen negociado"},
                    },
                },
                "qlib_features": {
                    "bsonType": ["object", "null"],
                    "properties": {
                        "feature_vector": {"bsonType": "binData", "description": "Vector binario de Alpha Factors"},
                        "factor_names": {"bsonType": "array", "items": {"bsonType": "string"}},
                    },
                },
                "master_inference": {
                    "bsonType": ["object", "null"],
                    "properties": {
                        "raw_tensors": {"bsonType": "binData", "description": "Tensores binarios de MASTER"},
                        "trend": {"bsonType": "string", "enum": ["BULLISH", "BEARISH", "NEUTRAL"]},
                    },
                },
                "galformer_inference": {
                    "bsonType": ["object", "null"],
                    "properties": {
                        "raw_tensors": {"bsonType": "binData", "description": "Tensores binarios de Galformer"},
                        "projected_horizon": {"bsonType": "double"},
                    },
                },
                "statistical_validation": {
                    "bsonType": "object",
                    "required": ["z_score", "p_value", "is_significant", "final_signal"],
                    "properties": {
                        "z_score": {"bsonType": "double"},
                        "p_value": {"bsonType": "double"},
                        "is_significant": {"bsonType": "bool"},
                        "final_signal": {"bsonType": "string", "enum": ["BUY", "SELL", "HOLD"]},
                    },
                },
            },
        }
    }

    try:
        db.create_collection(ticks_col_name, validator=ticks_validator)
        logger.info(f"Colección '{ticks_col_name}' creada con JSON Schema Validator.")
    except CollectionInvalid:
        logger.info(f"La colección '{ticks_col_name}' ya existe. Aplicando validador actualizado...")
        db.command("collMod", ticks_col_name, validator=ticks_validator)

    # RNF-05: Índice compuesto en {ticker: 1, timestamp: -1}
    ticks_col = db[ticks_col_name]
    ticks_col.create_index(
        [("ticker", ASCENDING), ("timestamp", DESCENDING)],
        name="idx_ticker_timestamp",
        background=True,
    )
    logger.info(f"Índice compuesto '{ticks_col_name}.{{ticker: 1, timestamp: -1}}' creado.")

    # ==========================================================================
    # 2. Colección 'INTENT_PREDICTION_LOG' (Auditoría Conversacional)
    # ==========================================================================
    intent_col_name = "INTENT_PREDICTION_LOG"
    intent_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["timestamp", "raw_prompt", "classified_intent"],
            "properties": {
                "user_id": {"bsonType": ["string", "null"]},
                "timestamp": {"bsonType": "date"},
                "raw_prompt": {"bsonType": "string"},
                "classified_intent": {
                    "bsonType": "string",
                    "enum": ["INTENT_MACRO", "INTENT_SECTORIAL", "INTENT_ACTIVO"],
                },
                "parsed_amount": {"bsonType": ["double", "null"]},
                "parsed_sector": {"bsonType": ["string", "null"]},
                "parsed_ticker": {"bsonType": ["string", "null"]},
                "execution_time_ms": {"bsonType": "int"},
            },
        }
    }

    try:
        db.create_collection(intent_col_name, validator=intent_validator)
        logger.info(f"Colección '{intent_col_name}' creada con JSON Schema Validator.")
    except CollectionInvalid:
        logger.info(f"La colección '{intent_col_name}' ya existe. Aplicando validador...")
        db.command("collMod", intent_col_name, validator=intent_validator)

    intent_col = db[intent_col_name]
    intent_col.create_index([("timestamp", DESCENDING)], name="idx_intent_timestamp", background=True)
    logger.info(f"Índice '{intent_col_name}.{{timestamp: -1}}' creado.")

    logger.info(f"=== Base de datos MongoDB '{db_name}' lista y configurada al 100% ===")
    return True


if __name__ == "__main__":
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database = os.getenv("MONGO_DB", "mps_market_db")
    success = initialize_mongo(mongo_uri=uri, db_name=database)
    sys.exit(0 if success else 1)
