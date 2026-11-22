/**
 * Entidad de Dominio: Prediction (AssetRecommendation)
 * Representa una recomendación puntual sobre un activo emitida por el pipeline cuantitativo.
 */
export class Prediction {
  constructor({
    ticker,
    price = 0,
    signal = 'HOLD',
    zScore = 0,
    pValue = 1.0,
    weightPct = 0,
    stopLoss = 0,
    takeProfit = 0,
    explanation = ''
  }) {
    this.ticker = ticker;
    this.price = Number(price);
    this.signal = signal;
    this.zScore = Number(zScore);
    this.pValue = Number(pValue);
    this.weightPct = Number(weightPct);
    this.stopLoss = Number(stopLoss);
    this.takeProfit = Number(takeProfit);
    this.explanation = explanation;
  }

  get isSignificant() {
    return this.pValue < 0.05;
  }

  get formattedPrice() {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(this.price);
  }
}
