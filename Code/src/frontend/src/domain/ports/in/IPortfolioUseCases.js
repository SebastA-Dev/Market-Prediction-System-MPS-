/**
 * Puertos de Entrada para Inversiones y Portafolio (Inbound Ports)
 */

export class IGetPortfolioUseCase {
  /**
   * @returns {Promise<import('../../models/PortfolioItem.js').PortfolioItem[]>}
   */
  async execute() {
    throw new Error('Método no implementado');
  }
}

export class IDeletePortfolioItemUseCase {
  /**
   * @param {string} ticker
   * @returns {Promise<boolean>}
   */
  async execute(ticker) {
    throw new Error('Método no implementado');
  }
}

export class ISavePortfolioItemUseCase {
  /**
   * @param {import('../../models/PortfolioItem.js').PortfolioItem} item
   * @returns {Promise<import('../../models/PortfolioItem.js').PortfolioItem>}
   */
  async execute(item) {
    throw new Error('Método no implementado');
  }
}
