/**
 * Puerto de Salida (Outbound Port): IPortfolioRepositoryPort
 * Contrato para acceder a la gestión de portafolio e inversiones del usuario en el backend.
 */
export class IPortfolioRepositoryPort {
  /**
   * @param {string} token
   * @returns {Promise<import('../../models/PortfolioItem.js').PortfolioItem[]>}
   */
  async getPortfolio(token) {
    throw new Error('Método no implementado');
  }

  /**
   * @param {string} ticker
   * @param {string} token
   * @returns {Promise<boolean>}
   */
  async deleteFromPortfolio(ticker, token) {
    throw new Error('Método no implementado');
  }

  /**
   * @param {import('../../models/PortfolioItem.js').PortfolioItem} item
   * @param {string} token
   * @returns {Promise<import('../../models/PortfolioItem.js').PortfolioItem>}
   */
  async saveToPortfolio(item, token) {
    throw new Error('Método no implementado');
  }
}
