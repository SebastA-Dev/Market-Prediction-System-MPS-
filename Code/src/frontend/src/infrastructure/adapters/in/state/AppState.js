/**
 * Adaptador de Entrada: AppState
 * Gestor de estado reactivo desacoplado para la interfaz gráfica.
 */
export class AppState {
  constructor() {
    this.state = {
      currentView: 'advisor', // 'advisor' | 'guide'
      user: null,
      isLoading: false,
      loadingMessage: 'Procesando Modelo Cuantitativo MASTER',
      loadingSubtext: 'Corriendo 10,000 simulaciones Monte Carlo y estructurando órdenes de compra...',
      predictionIntent: null,
      activeSector: null,
      portfolio: [],
      notifications: [],
      isNotifMenuOpen: false,
      isUserModalOpen: false,
      userModalTab: 'tracked', // 'tracked' | 'settings' | 'auth'
      isTrustDrawerOpen: false,
      trustScenario: 'allweather',
      lastError: null,
      toasts: []
    };

    this.listeners = new Set();
  }

  get() {
    return this.state;
  }

  set(partialState) {
    this.state = { ...this.state, ...partialState };
    this.notify();
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify() {
    for (const listener of this.listeners) {
      try {
        listener(this.state);
      } catch (err) {
        console.error('Error en listener de AppState:', err);
      }
    }
  }

  showToast(message, type = 'info') {
    const toast = {
      id: Date.now() + Math.random(),
      message,
      type
    };
    this.set({ toasts: [...this.state.toasts, toast] });

    setTimeout(() => {
      this.set({ toasts: this.state.toasts.filter(t => t.id !== toast.id) });
    }, 3500);
  }
}

export const globalAppState = new AppState();
