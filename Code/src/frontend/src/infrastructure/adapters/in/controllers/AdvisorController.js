import { globalAppState } from '../state/AppState.js';
import { PortfolioItem } from '../../../../domain/models/PortfolioItem.js';

/**
 * Controlador de Entrada (Primary Adapter): AdvisorController
 * Orquesta las interacciones de la vista del Consejero IA con los servicios de aplicación.
 */
export class AdvisorController {
  /**
   * @param {import('../../../../application/PredictIntentService.js').PredictIntentService} predictService
   * @param {import('../../../../application/PortfolioApplicationService.js').PortfolioApplicationService} portfolioService
   */
  constructor(predictService, portfolioService) {
    this.predictService = predictService;
    this.portfolioService = portfolioService;
  }

  /**
   * Cambia la vista activa ('advisor' | 'guide').
   * @param {'advisor' | 'guide'} viewName
   */
  switchView(viewName) {
    globalAppState.set({ currentView: viewName });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /**
   * Procesa la consulta en lenguaje natural del usuario (UC-01, UC-02).
   * Llama a POST /api/v1/predict/intent en el backend FastAPI.
   * @param {string} promptText
   */
  async submitPrompt(promptText) {
    if (!promptText || !promptText.trim()) {
      globalAppState.showToast('Por favor ingresa una consulta o monto de inversión.', 'info');
      return;
    }

    const state = globalAppState.get();
    globalAppState.set({
      isLoading: true,
      lastError: null,
      activeSector: null
    });

    try {
      const intentResult = await this.predictService.execute(promptText, state.user?.id || null);
      
      globalAppState.set({
        isLoading: false,
        predictionIntent: intentResult,
        lastError: null
      });

      // Feedback al usuario
      globalAppState.showToast(`¡Plan generado con éxito! (${intentResult.executionTimeMs} ms)`, 'success');
      
      // Desplazamiento suave hacia los resultados
      setTimeout(() => {
        const resultsEl = document.getElementById('results-container');
        if (resultsEl) resultsEl.scrollIntoView({ behavior: 'smooth' });
      }, 100);

    } catch (err) {
      console.error('Error procesando intención de inversión:', err);
      
      let userFriendlyMsg = err.message || 'No se pudo comunicar con el servicio analítico de IA.';
      if (err.status === 400) {
        // Mensaje de aclaración del clasificador de lenguaje natural (RF-20)
        userFriendlyMsg = err.message;
      } else if (err.status === 408) {
        userFriendlyMsg = 'Tiempo de espera agotado al conectar con el motor analítico.';
      } else if (!err.status || err.message.includes('Failed to fetch')) {
        userFriendlyMsg = 'Servicio Python FastAPI no disponible en http://localhost:8000. Inicia el servidor o revisa la conexión.';
      }

      globalAppState.set({
        isLoading: false,
        lastError: userFriendlyMsg
      });

      globalAppState.showToast(userFriendlyMsg, 'info');
    }
  }

  /**
   * Navega hacia el desglose de un sector específico (Micro-nivel).
   * @param {string} sectorId
   */
  selectSector(sectorId) {
    globalAppState.set({ activeSector: sectorId });
    setTimeout(() => {
      const resultsEl = document.getElementById('results-container');
      if (resultsEl) resultsEl.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  }

  /**
   * Vuelve a la vista general macro del portafolio.
   */
  resetToMacro() {
    globalAppState.set({ activeSector: null });
    setTimeout(() => {
      const resultsEl = document.getElementById('results-container');
      if (resultsEl) resultsEl.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  }

  /**
   * Alterna el seguimiento de un activo (marcar como invertido o eliminar).
   * @param {Object} assetData
   */
  async toggleTrackAsset(assetData) {
    const state = globalAppState.get();
    const existing = state.portfolio.find(p => p.ticker.toUpperCase() === assetData.ticker.toUpperCase());

    if (existing) {
      try {
        await this.portfolioService.deleteItem(existing.ticker);
        const updatedPortfolio = await this.portfolioService.getPortfolio();
        globalAppState.set({ portfolio: updatedPortfolio });
        globalAppState.showToast(`Posición ${existing.ticker} removida de tu portafolio guardado.`, 'info');
      } catch (err) {
        globalAppState.showToast(`Error al remover: ${err.message}`, 'info');
      }
    } else {
      try {
        const newItem = new PortfolioItem({
          id: assetData.id || `track-${assetData.ticker.toLowerCase()}`,
          name: assetData.name,
          ticker: assetData.ticker,
          sector: assetData.sector || 'General',
          amount: assetData.amount || 0,
          status: 'Invertido',
          change: '+0.0%'
        });

        await this.portfolioService.saveItem(newItem);
        const updatedPortfolio = await this.portfolioService.getPortfolio();
        globalAppState.set({ portfolio: updatedPortfolio });
        globalAppState.showToast(`¡${newItem.ticker} marcado como INVERTIDO y agregado a tu perfil!`, 'success');
      } catch (err) {
        globalAppState.showToast(`Error al guardar: ${err.message}`, 'info');
      }
    }
  }

  /**
   * Abre el drawer de auditoría algorítmica y confianza.
   * @param {string} scenario
   */
  openTrustDrawer(scenario = 'allweather') {
    globalAppState.set({
      isTrustDrawerOpen: true,
      trustScenario: scenario
    });
  }

  closeTrustDrawer() {
    globalAppState.set({ isTrustDrawerOpen: false });
  }
}
