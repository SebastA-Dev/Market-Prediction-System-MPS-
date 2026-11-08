"""
Módulo de Gestión de Riesgo Cuantitativo y Explicabilidad.
Calcula umbrales sugeridos de Stop-Loss y Take-Profit (RF-40, UC-07)
y genera justificaciones en lenguaje estrictamente probabilístico y condicional (RF-35, RNF-19).
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from ...models.market import SignalType


class RiskManagementService:
    """
    Calcula parámetros de mitigación de riesgo técnico (Stop-Loss y Take-Profit)
    basados en el Rango Verdadero Promedio (ATR) y volatilidad histórica.
    """

    @staticmethod
    def calculate_risk_levels(
        current_price: float,
        df_clean: pd.DataFrame,
        signal: SignalType,
        atr_multiplier_stop: float = 1.5,
        atr_multiplier_profit: float = 2.5,
    ) -> Tuple[float, float, str]:
        """
        Calcula los niveles de Stop-loss y Take-profit.
        Retorna (stop_loss, take_profit, explicacion_condicional).
        """
        if current_price <= 0 or df_clean.empty or len(df_clean) < 14:
            return round(current_price * 0.95, 2), round(current_price * 1.05, 2), "Niveles referenciales por defecto."

        # Cálculo de ATR de 14 periodos
        high = df_clean["High"]
        low = df_clean["Low"]
        close = df_clean["Close"]
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
        atr = float(tr.tail(14).mean())
        if atr <= 0 or np.isnan(atr):
            atr = current_price * 0.02

        if signal == SignalType.BUY:
            stop_loss = max(0.01, current_price - (atr * atr_multiplier_stop))
            take_profit = current_price + (atr * atr_multiplier_profit)
            explanation = (
                f"Bajo un escenario favorable proyectado con volatilidad ATR de {atr:.2f}, "
                f"un umbral de mitigación en {stop_loss:.2f} limitaría la exposición ante reversiones, "
                f"mientras que un objetivo condicional en {take_profit:.2f} captura la extensión esperada."
            )
        elif signal == SignalType.SELL:
            stop_loss = current_price + (atr * atr_multiplier_stop)
            take_profit = max(0.01, current_price - (atr * atr_multiplier_profit))
            explanation = (
                f"En presencia de indicios correctivos con banda de volatilidad ATR de {atr:.2f}, "
                f"un tope de salida en {stop_loss:.2f} acota el riesgo alcista, "
                f"estableciendo una zona tentativa de cobertura en {take_profit:.2f}."
            )
        else:  # HOLD
            stop_loss = current_price - (atr * atr_multiplier_stop)
            take_profit = current_price + (atr * atr_multiplier_profit)
            explanation = (
                "La serie no exhibe dispersión estadística concluyente frente al ruido aleatorio. "
                "Se sugiere mantener postura observadora hasta la conformación de una pauta significativa."
            )

        return round(stop_loss, 2), round(take_profit, 2), explanation
