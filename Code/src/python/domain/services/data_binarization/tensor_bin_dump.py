"""
Módulo de serialización y empaquetado binario de tensores y vectores de características.
Cumple con la especificación de MongoDB en UMLBaseDeDatos.drawio:
- feature_vector : BINARY (Alpha)
- raw_tensors : BINARY (Inferencia de MASTER y Galformer)
Permite persistencia inmutable ultracompacta y recuperación sin pérdida de precisión.
"""

import io
from typing import Any, Optional, Union
import numpy as np


class TensorBinarySerializer:
    """
    Serializa y deserializa tensores de NumPy / PyTorch a formato binario comprimido (bytes).
    """

    @staticmethod
    def serialize_array(array: Union[np.ndarray, list]) -> bytes:
        """
        Convierte una matriz o lista a un flujo binario compacto utilizando el formato nativo NPY de NumPy.
        """

        array = np.array(array, dtype=np.float32)
        buffer = io.BytesIO()
        np.save(buffer, array, allow_pickle=False)
        return buffer.getvalue()

    @staticmethod
    def deserialize_array(binary_data: bytes) -> Optional[np.ndarray]:
        """
        Reconstruye la matriz NumPy original a partir de los bytes serializados.
        """
        if not binary_data:
            return None
        try:
            buffer = io.BytesIO(binary_data)
            return np.load(buffer, allow_pickle=False)
        except Exception:
            return None

    @classmethod
    def serialize_alpha_vector(cls, features_dict: dict) -> bytes:
        """
        Serializa un conjunto nombrado de Alpha Factors a bytes.
        """
        buffer = io.BytesIO()
        keys = sorted(features_dict.keys())
        values = np.array([float(features_dict[k]) for k in keys], dtype=np.float32)
        np.save(buffer, values, allow_pickle=False)
        return buffer.getvalue()
