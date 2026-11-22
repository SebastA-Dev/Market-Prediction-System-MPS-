import { INotificationRepositoryPort } from '../../../domain/ports/out/INotificationAndStoragePorts.js';
import { ApiConfig } from '../../../config/ApiConfig.js';
import { HttpClient } from '../../http/HttpClient.js';

/**
 * Adaptador Secundario (Outbound Adapter): NotificationRestAdapter
 * Estructura de integración preparada para consultar el historial de alertas y notificaciones.
 */
export class NotificationRestAdapter extends INotificationRepositoryPort {
  /**
   * @param {HttpClient} [httpClient]
   */
  constructor(httpClient = null) {
    super();
    this.http = httpClient || new HttpClient(ApiConfig.MICRONAUT_BASE_URL);
  }

  /**
   * Consulta las notificaciones y alertas disparadas para el usuario (UC-10, RF-27).
   * 
   * Método HTTP esperado: GET
   * Propósito: Consultar el historial de alertas disparadas desde la tabla alert_history en PostgreSQL.
   * 
   * @param {string} token
   * @returns {Promise<import('../../../domain/models/Notification.js').Notification[]>}
   */
  async fetchNotifications(token) {
    // TODO: Colocar URL hacia el endpoint
    // Método esperado: GET
    // Propósito: Consultar historial de señales disparadas asociadas a alert_history (UC-10, RF-27)
    const endpointUrl = null; // Pendiente de implementación en el microservicio

    if (!endpointUrl) {
      return [];
    }

    const response = await this.http.get(endpointUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    return response;
  }

  /**
   * Marca las notificaciones como leídas o las elimina.
   * 
   * Método HTTP esperado: DELETE o POST
   * Propósito: Limpiar o marcar como leídas las alertas en la base de datos.
   * 
   * @param {string} token
   * @returns {Promise<boolean>}
   */
  async clearNotifications(token) {
    // TODO: Colocar URL hacia el endpoint
    // Método esperado: DELETE
    // Propósito: Limpiar o marcar como leídas las alertas del usuario
    const endpointUrl = null; // Pendiente de implementación en el microservicio

    if (!endpointUrl) {
      return true;
    }

    await this.http.delete(endpointUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    return true;
  }
}
