/**
 * Entidad de Dominio: PortfolioItem
 * Representa una inversión seguida/guardada por el usuario en su portafolio.
 */
export class PortfolioItem {
  constructor({
    id,
    ticker,
    name,
    sector = 'General',
    amount = 0,
    status = 'Invertido',
    active = true,
    alertsEnabled = true,
    followingSince = null,
    change = '+0.0%'
  }) {
    this.id = id || `item-${ticker.toLowerCase()}`;
    this.ticker = (ticker || '').toUpperCase();
    this.name = name || ticker;
    this.sector = sector;
    this.amount = Number(amount) || 0;
    this.status = status;
    this.active = active;
    this.alertsEnabled = alertsEnabled;
    this.followingSince = followingSince || new Date().toISOString().split('T')[0];
    this.change = change;
  }

  get formattedAmount() {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(this.amount);
  }
}
