import { INotificationsUseCase } from '../domain/ports/in/INotificationsUseCases.js';
import { Notification } from '../domain/models/Notification.js';

/**
 * Servicio de Aplicación: NotificationApplicationService
 * Gestiona la carga y actualización de notificaciones del sistema.
 */
export class NotificationApplicationService extends INotificationsUseCase {
  /**
   * @param {import('../domain/ports/out/INotificationAndStoragePorts.js').INotificationRepositoryPort} notificationRepository
   * @param {import('../domain/ports/out/INotificationAndStoragePorts.js').IStoragePort} storagePort
   */
  constructor(notificationRepository, storagePort) {
    super();
    this.notificationRepository = notificationRepository;
    this.storagePort = storagePort;
  }

  async getNotifications() {
    const token = this.storagePort.getItem('mps_auth_token');
    if (token) {
      try {
        return await this.notificationRepository.fetchNotifications(token);
      } catch (err) {
        console.info('Notificaciones remotas no disponibles aún:', err.message);
      }
    }

    const cached = this.storagePort.getItem('mps_notifications_cache');
    if (cached) {
      try {
        const raw = JSON.parse(cached);
        return raw.map(n => new Notification(n));
      } catch (e) {
        // Fallback
      }
    }

    const defaults = [
      new Notification({
        id: 1,
        ticker: 'META',
        title: 'Aumento de FCF Yield',
        desc: 'Meta Platforms reportó incremento de Flujo Libre a 4.9%.',
        time: 'Hace 2 horas',
        read: false
      }),
      new Notification({
        id: 2,
        ticker: 'AAPL',
        title: 'Confirmación de Dividendo',
        desc: 'Apple confirmó pago trimestral de $0.25/acción.',
        time: 'Hace 5 horas',
        read: false
      }),
      new Notification({
        id: 3,
        ticker: 'BIL',
        title: 'Interés acumulado',
        desc: 'Rendimiento T-Bill acreditado en tasa anual de 5.15%.',
        time: 'Ayer',
        read: false
      })
    ];
    this.storagePort.setItem('mps_notifications_cache', JSON.stringify(defaults));
    return defaults;
  }

  async clearNotifications() {
    const token = this.storagePort.getItem('mps_auth_token');
    if (token) {
      try {
        await this.notificationRepository.clearNotifications(token);
      } catch (e) {
        // Ignorar
      }
    }
    this.storagePort.setItem('mps_notifications_cache', JSON.stringify([]));
  }
}
