import { globalAppState } from '../state/AppState.js';

/**
 * Controlador de Entrada (Primary Adapter): NotificationController
 * Gestiona el menú desplegable y acciones sobre notificaciones.
 */
export class NotificationController {
  /**
   * @param {import('../../../../application/NotificationApplicationService.js').NotificationApplicationService} notifService
   */
  constructor(notifService) {
    this.notifService = notifService;
  }

  async loadNotifications() {
    try {
      const items = await this.notifService.getNotifications();
      globalAppState.set({ notifications: items });
    } catch (err) {
      console.warn('Error cargando notificaciones:', err);
    }
  }

  toggleMenu() {
    const current = globalAppState.get().isNotifMenuOpen;
    globalAppState.set({ isNotifMenuOpen: !current });
    if (!current) {
      this.loadNotifications();
    }
  }

  async clearAll() {
    try {
      await this.notifService.clearNotifications();
      globalAppState.set({ notifications: [] });
      globalAppState.showToast('Notificaciones marcadas como leídas.', 'success');
    } catch (err) {
      globalAppState.showToast('Error al limpiar notificaciones', 'info');
    }
  }
}
