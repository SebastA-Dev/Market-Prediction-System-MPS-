/**
 * Puerto de Entrada (Inbound Port): IPredictIntentUseCase
 * Caso de uso para clasificar intenciones de inversión y generar recomendaciones cuantitativas (UC-01, UC-02).
 */
export class IPredictIntentUseCase {
  /**
   * @param {string} prompt - Consulta en lenguaje natural
   * @param {string|null} userId - ID opcional del usuario
   * @returns {Promise<import('../../models/PredictionIntent.js').PredictionIntent>}
   */
  async execute(prompt, userId = null) {
    throw new Error('Método no implementado');
  }
}
