import { IPortfolioRepositoryPort } from '../../../domain/ports/out/IPortfolioRepositoryPort.js';
import { PortfolioItem } from '../../../domain/models/PortfolioItem.js';
import { ApiConfig } from '../../../config/ApiConfig.js';
import { HttpClient } from '../../http/HttpClient.js';

/**
 * Adaptador Secundario (Outbound Adapter): MicronautPortfolioAdapter
 * Se comunica con el microservicio Java Micronaut para gestionar inversiones y seguimiento.
 */
export class MicronautPortfolioAdapter extends IPortfolioRepositoryPort {
  /**
   * @param {HttpClient} [httpClient]
   */
  constructor(httpClient = null) {
    super();
    this.http = httpClient || new HttpClient(ApiConfig.MICRONAUT_BASE_URL);
  }

  /**
   * Obtiene la lista de activos seguidos por el usuario dueño del JWT.
   * Conectado a GET /api/v1/portfolio (Micronaut InvestmentController).
   * @param {string} token
   * @returns {Promise<PortfolioItem[]>}
   */
  async getPortfolio(token) {
    if (!token) {
      throw new Error('Se requiere autenticación para consultar el portafolio remoto.');
    }

    const response = await this.http.get(ApiConfig.endpoints.getPortfolio, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const assets = response.assets || [];
    return assets.map(a => new PortfolioItem({
      id: `asset-${a.ticker.toLowerCase()}`,
      ticker: a.ticker,
      name: a.name,
      sector: a.sector,
      amount: a.amount || 0,
      active: a.active,
      alertsEnabled: a.alertsEnabled,
      followingSince: a.followingSince ? a.followingSince.split('T')[0] : null
    }));
  }

  /**
   * Deja de seguir un activo del portafolio.
   * Conectado a DELETE /api/v1/portfolio/{ticker} (Micronaut InvestmentController).
   * @param {string} ticker
   * @param {string} token
   * @returns {Promise<boolean>}
   */
  async deleteFromPortfolio(ticker, token) {
    if (!token) {
      throw new Error('Se requiere autenticación para eliminar un activo del portafolio.');
    }

    const path = ApiConfig.endpoints.deletePortfolioItem(ticker);
    await this.http.delete(path, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    return true;
  }

  /**
   * Registra una nueva inversión o activo para seguimiento en el portafolio del usuario.
   * Estructura preparada bajo arquitectura hexagonal para la posterior integración con el backend.
   * 
   * Método HTTP esperado: POST
   * Propósito: Persistir un nuevo activo en user_configuration para el usuario autenticado (UC-09b, RF-22).
   * 
   * @param {PortfolioItem} item
   * @param {string} token
   * @returns {Promise<PortfolioItem>}
   */
  async saveToPortfolio(item, token) {
    // TODO: Colocar URL hacia el endpoint
    // Método esperado: POST
    // Propósito: Suscribir/agregar activo al portafolio del usuario en la base relacional
    const endpointUrl = null; // Pendiente de implementación en el backend

    if (!endpointUrl) {
      // Se mantiene la estructura y se devuelve la entidad de dominio local
      return item;
    }

    const payload = {
      ticker: item.ticker,
      amount: item.amount,
      alertsEnabled: item.alertsEnabled
    };

    const response = await this.http.post(endpointUrl, payload, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    return new PortfolioItem(response);
  }
}
