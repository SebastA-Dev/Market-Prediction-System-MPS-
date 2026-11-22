/**
 * Puertos de Entrada para Notificaciones (Inbound Ports)
 */

export class INotificationsUseCase {
  /**
   * @returns {Promise<import('../../models/Notification.js').Notification[]>}
   */
  async getNotifications() {
    throw new Error('Método no implementado');
  }

  /**
   * @returns {Promise<void>}
   */
  async clearNotifications() {
    throw new Error('Método no implementado');
  }
}
