/**
 * Puerto de Salida (Outbound Port): INotificationRepositoryPort
 * Contrato para acceder al historial de alertas y notificaciones del usuario.
 */
export class INotificationRepositoryPort {
  /**
   * @param {string} token
   * @returns {Promise<import('../../models/Notification.js').Notification[]>}
   */
  async fetchNotifications(token) {
    throw new Error('Método no implementado');
  }

  /**
   * @param {string} token
   * @returns {Promise<boolean>}
   */
  async clearNotifications(token) {
    throw new Error('Método no implementado');
  }
}

/**
 * Puerto de Salida (Outbound Port): IStoragePort
 * Contrato para el almacenamiento persistente en el navegador.
 */
export class IStoragePort {
  getItem(key) {
    throw new Error('Método no implementado');
  }
  setItem(key, value) {
    throw new Error('Método no implementado');
  }
  removeItem(key) {
    throw new Error('Método no implementado');
  }
}
