import { IPredictionRepositoryPort } from '../../../domain/ports/out/IPredictionRepositoryPort.js';
import { PredictionIntent } from '../../../domain/models/PredictionIntent.js';
import { Prediction } from '../../../domain/models/Prediction.js';
import { ApiConfig } from '../../../config/ApiConfig.js';
import { HttpClient } from '../../http/HttpClient.js';

/**
 * Adaptador Secundario (Outbound Adapter): FastApiPredictionAdapter
 * Se comunica directamente con el microservicio Python FastAPI (RF-17 a RF-20, UC-01, UC-02).
 */
export class FastApiPredictionAdapter extends IPredictionRepositoryPort {
  /**
   * @param {HttpClient} [httpClient]
   */
  constructor(httpClient = null) {
    super();
    this.http = httpClient || new HttpClient(ApiConfig.FASTAPI_BASE_URL);
  }

  /**
   * Envía la intención del usuario a POST /api/v1/predict/intent en FastAPI.
   * @param {string} prompt
   * @param {string|null} userId
   * @returns {Promise<PredictionIntent>}
   */
  async predictIntent(prompt, userId = null) {
    // Extraer presupuesto si viene en el texto para enriquecer la entidad de dominio
    const match = prompt.match(/\d+[\d,]*/);
    let requestedAmount = 20000;
    if (match) {
      const parsed = parseInt(match[0].replace(/,/g, ''), 10);
      if (!isNaN(parsed) && parsed > 0) requestedAmount = parsed;
    }

    const payload = {
      prompt: prompt,
      user_id: userId || undefined
    };

    const response = await this.http.post(ApiConfig.endpoints.predictIntent, payload, {
      timeout: ApiConfig.timeouts.predict
    });

    const recommendations = (response.recommendations || []).map(r => new Prediction({
      ticker: r.ticker,
      price: r.price,
      signal: r.signal,
      zScore: r.z_score ?? r.zScore,
      pValue: r.p_value ?? r.pValue,
      weightPct: r.weight_pct ?? r.weightPct,
      stopLoss: r.stop_loss ?? r.stopLoss,
      takeProfit: r.take_profit ?? r.takeProfit,
      explanation: r.explanation
    }));

    return new PredictionIntent({
      classifiedIntent: response.classified_intent,
      confidenceStatement: response.confidence_statement,
      macroContext: response.macro_context,
      allocationChart: response.allocation_chart || {},
      recommendations,
      executionTimeMs: response.execution_time_ms || 0,
      requestedAmount,
      rawPrompt: prompt
    });
  }
}
