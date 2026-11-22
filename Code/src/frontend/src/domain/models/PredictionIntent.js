import { Prediction } from './Prediction.js';

/**
 * Entidad de Dominio: PredictionIntent (IntentResponse)
 * Resultado completo devuelto por el clasificador de intención y pipeline cuantitativo (RF-17 a RF-20).
 */
export class PredictionIntent {
  constructor({
    classifiedIntent = 'INTENT_MACRO',
    confidenceStatement = '',
    macroContext = null,
    allocationChart = {},
    recommendations = [],
    executionTimeMs = 0,
    requestedAmount = 20000,
    rawPrompt = ''
  }) {
    this.classifiedIntent = classifiedIntent;
    this.confidenceStatement = confidenceStatement;
    this.macroContext = macroContext;
    this.allocationChart = allocationChart;
    this.recommendations = recommendations.map(r => r instanceof Prediction ? r : new Prediction(r));
    this.executionTimeMs = executionTimeMs;
    this.requestedAmount = requestedAmount;
    this.rawPrompt = rawPrompt;
  }

  get isMacro() {
    return this.classifiedIntent === 'INTENT_MACRO';
  }

  get isSectorial() {
    return this.classifiedIntent === 'INTENT_SECTORIAL';
  }

  get isAsset() {
    return this.classifiedIntent === 'INTENT_ACTIVO';
  }

  get formattedTotalAmount() {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(this.requestedAmount);
  }
}
