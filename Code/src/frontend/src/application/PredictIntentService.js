import { IPredictIntentUseCase } from '../domain/ports/in/IPredictIntentUseCase.js';
import { PredictionIntent } from '../domain/models/PredictionIntent.js';

/**
 * Servicio de Aplicación: PredictIntentService
 * Implementa el caso de uso UC-01 y UC-02 para interactuar con el modelo predictivo.
 */
export class PredictIntentService extends IPredictIntentUseCase {
  /**
   * @param {import('../domain/ports/out/IPredictionRepositoryPort.js').IPredictionRepositoryPort} predictionRepository
   */
  constructor(predictionRepository) {
    super();
    this.predictionRepository = predictionRepository;
  }

  /**
   * Ejecuta la predicción sobre el prompt ingresado.
   * @param {string} prompt
   * @param {string|null} userId
   * @returns {Promise<PredictionIntent>}
   */
  async execute(prompt, userId = null) {
    if (!prompt || typeof prompt !== 'string' || !prompt.trim()) {
      throw new Error('El texto de consulta no puede estar vacío.');
    }

    return await this.predictionRepository.predictIntent(prompt.trim(), userId);
  }
}
