import {
  IGetPortfolioUseCase,
  IDeletePortfolioItemUseCase,
  ISavePortfolioItemUseCase
} from '../domain/ports/in/IPortfolioUseCases.js';
import { PortfolioItem } from '../domain/models/PortfolioItem.js';

/**
 * Servicio de Aplicación: PortfolioApplicationService
 * Gestiona las operaciones de portafolio respetando los puertos y adaptadores.
 */
export class PortfolioApplicationService {
  /**
   * @param {import('../domain/ports/out/IPortfolioRepositoryPort.js').IPortfolioRepositoryPort} portfolioRepository
   * @param {import('../domain/ports/out/INotificationAndStoragePorts.js').IStoragePort} storagePort
   */
  constructor(portfolioRepository, storagePort) {
    this.portfolioRepository = portfolioRepository;
    this.storagePort = storagePort;
  }

  _getToken() {
    return this.storagePort.getItem('mps_auth_token') || null;
  }

  /**
   * Obtiene la lista de inversiones del portafolio.
   * Si el usuario está autenticado, consulta el endpoint real de Micronaut GET /api/v1/portfolio.
   * Si no, recupera las inversiones locales guardadas en storage.
   * @returns {Promise<PortfolioItem[]>}
   */
  async getPortfolio() {
    const token = this._getToken();
    if (token) {
      const remoteItems = await this.portfolioRepository.getPortfolio(token);
      // Una sesión autenticada solo muestra datos remotos de esa cuenta.
      this.storagePort.setItem('mps_portfolio_cache', JSON.stringify(remoteItems));
      return remoteItems;
    }

    const cached = this.storagePort.getItem('mps_portfolio_cache');
    if (cached) {
      try {
        const raw = JSON.parse(cached);
        return raw.map(i => new PortfolioItem(i));
      } catch (e) {
        // Fallback a lista inicial
      }
    }

    // Datos base por defecto para experiencia inicial
    const defaultItems = [
      new PortfolioItem({
        id: 'tech-allweather',
        name: 'Sector Tecnología e IA',
        ticker: 'TECH-SECTOR',
        amount: 7000,
        status: 'Invertido',
        followingSince: '2026-08-10',
        change: '+3.4%'
      }),
      new PortfolioItem({
        id: 'sp500-allweather',
        name: 'S&P 500 Indexado',
        ticker: 'VOO',
        amount: 4000,
        status: 'Guardado',
        followingSince: '2026-08-12',
        change: '+1.1%'
      })
    ];
    this.storagePort.setItem('mps_portfolio_cache', JSON.stringify(defaultItems));
    return defaultItems;
  }

  /**
   * Elimina un activo del portafolio del usuario.
   * Conecta con DELETE /api/v1/portfolio/{ticker} en Micronaut cuando hay sesión.
   * @param {string} ticker
   * @returns {Promise<boolean>}
   */
  async deleteItem(ticker) {
    const token = this._getToken();
    if (token) {
      await this.portfolioRepository.deleteFromPortfolio(ticker, token);
    }

    // Actualizar storage local
    const items = await this.getPortfolio();
    const filtered = items.filter(i => i.ticker.toUpperCase() !== ticker.toUpperCase());
    this.storagePort.setItem('mps_portfolio_cache', JSON.stringify(filtered));
    return true;
  }

  /**
   * Agrega o marca un activo como invertido.
   * Invoca el puerto de guardado de portafolio.
   * @param {PortfolioItem} item
   * @returns {Promise<PortfolioItem>}
   */
  async saveItem(item) {
    const token = this._getToken();
    let saved = item;

    try {
      saved = await this.portfolioRepository.saveToPortfolio(item, token);
    } catch (error) {
      console.info('Guardando en almacenamiento local:', error.message);
    }

    const items = await this.getPortfolio();
    const existingIndex = items.findIndex(i => i.ticker.toUpperCase() === item.ticker.toUpperCase());
    if (existingIndex >= 0) {
      items[existingIndex] = saved;
    } else {
      items.push(saved);
    }
    this.storagePort.setItem('mps_portfolio_cache', JSON.stringify(items));
    return saved;
  }
}
