/**
 * Puerto de Salida (Outbound Port): IPredictionRepositoryPort
 * Contrato para comunicarse con el servicio analítico cuantitativo (FastAPI).
 */
export class IPredictionRepositoryPort {
  /**
   * @param {string} prompt
   * @param {string|null} userId
   * @returns {Promise<import('../../models/PredictionIntent.js').PredictionIntent>}
   */
  async predictIntent(prompt, userId = null) {
    throw new Error('Método no implementado');
  }
}
