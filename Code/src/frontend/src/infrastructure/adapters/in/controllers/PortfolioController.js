import { globalAppState } from '../state/AppState.js';

/**
 * Controlador de Entrada (Primary Adapter): PortfolioController
 * Gestiona el modal de usuario y la lista de inversiones seguidas.
 */
export class PortfolioController {
  /**
   * @param {import('../../../../application/PortfolioApplicationService.js').PortfolioApplicationService} portfolioService
   */
  constructor(portfolioService) {
    this.portfolioService = portfolioService;
  }

  async loadPortfolio() {
    try {
      const items = await this.portfolioService.getPortfolio();
      globalAppState.set({ portfolio: items });
    } catch (err) {
      console.warn('Error cargando portafolio:', err);
    }
  }

  async deleteItem(ticker) {
    try {
      await this.portfolioService.deleteItem(ticker);
      const items = await this.portfolioService.getPortfolio();
      globalAppState.set({ portfolio: items });
      globalAppState.showToast(`Activo ${ticker} eliminado correctamente.`, 'info');
    } catch (err) {
      globalAppState.showToast(`Error al eliminar: ${err.message}`, 'info');
    }
  }

  openModal(tab = 'tracked') {
    this.loadPortfolio();
    globalAppState.set({
      isUserModalOpen: true,
      userModalTab: tab
    });
  }

  closeModal() {
    globalAppState.set({ isUserModalOpen: false });
  }

  switchTab(tab) {
    globalAppState.set({ userModalTab: tab });
  }
}
