/**
 * Entidad de Dominio: Notification
 * Representa una alerta o notificación de mercado / métricas para el usuario.
 */
export class Notification {
  constructor({ id, ticker, title, desc, time = 'Reciente', read = false }) {
    this.id = id;
    this.ticker = ticker;
    this.title = title;
    this.desc = desc;
    this.time = time;
    this.read = read;
  }
}
