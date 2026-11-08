"""
Validador Estadístico basado en Prueba de Hipótesis (Z-Test).
Aplica un filtro riguroso con nivel de significancia alpha = 0.05 sobre cada predicción generada.
Cumple estrictamente con:
- RF-09: Prueba de hipótesis Z-test con alpha = 0.05.
- RF-10: Emisión de BUY o SELL únicamente cuando |z| > 1.96 (p < 0.05).
- RF-11: Emisión de HOLD cuando z en [-1.96, 1.96].
- RF-12: Emisión de HOLD sin error cuando std == 0.
- RNF-20: Transparencia legal del indicador de consistencia.
"""

import math
from typing import Tuple
import numpy as np
from scipy import stats
from ...models.market import SignalType, StatisticalValidation


class StatisticalValidator:
    """
    Motor de validación estadística de hipótesis para señales predictivas.
    """

    CRITICAL_Z = 1.96  # Para alpha = 0.05 en prueba de dos colas
    ALPHA = 0.05

    @classmethod
    def validate_prediction(
        cls,
        predicted_return: float,
        historical_returns: np.ndarray,
    ) -> StatisticalValidation:
        """
        Evalúa si el retorno esperado proyectado por los modelos es estadísticamente
        significativo respecto a la distribución histórica del activo.
        
        Hipótesis Nula H0: El retorno proyectado proviene de la distribución media histórica (ruido).
        Hipótesis Alterna H1: El retorno proyectado difiere significativamente de H0.
        """
        # Verificación RF-12: Desviación estándar nula o datos insuficientes
        if historical_returns is None or len(historical_returns) < 2:
            return StatisticalValidation(
                z_score=0.0,
                p_value=1.0,
                is_significant=False,
                final_signal=SignalType.HOLD,
            )

        mean_hist = float(np.mean(historical_returns))
        std_hist = float(np.std(historical_returns, ddof=1))

        if math.isclose(std_hist, 0.0, abs_tol=1e-9) or math.isnan(std_hist):
            return StatisticalValidation(
                z_score=0.0,
                p_value=1.0,
                is_significant=False,
                final_signal=SignalType.HOLD,
            )

        # Cálculo del estadístico Z (normalizado por la desviación típica muestral)
        z_score = (predicted_return - mean_hist) / (std_hist + 1e-9)

        # Cálculo del p-value (dos colas) mediante distribución normal estándar
        p_value = 2.0 * (1.0 - stats.norm.cdf(abs(z_score)))

        # Verificación de umbral crítico
        is_significant = (abs(z_score) > cls.CRITICAL_Z) and (p_value < cls.ALPHA)

        if not is_significant:
            final_signal = SignalType.HOLD
        elif z_score > cls.CRITICAL_Z:
            final_signal = SignalType.BUY
        elif z_score < -cls.CRITICAL_Z:
            final_signal = SignalType.SELL
        else:
            final_signal = SignalType.HOLD

        return StatisticalValidation(
            z_score=round(float(z_score), 4),
            p_value=round(float(p_value), 5),
            is_significant=bool(is_significant),
            final_signal=final_signal,
        )
