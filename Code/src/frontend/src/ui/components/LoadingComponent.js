/**
 * Componente: LoadingComponent
 * Estado de carga con indicador animado del modelo cuantitativo (MASTER / Galformer).
 */
export class LoadingComponent {
  render(state) {
    if (!state.isLoading) return '';

    return `
      <div id="loading-state" class="flex flex-col items-center justify-center py-16 w-full max-w-xl text-center animate-fade-in">
        <div class="relative w-20 h-20 mb-6">
          <div class="absolute inset-0 rounded-full border-4 border-slate-800"></div>
          <div class="absolute inset-0 rounded-full border-4 border-fintech-emerald border-t-transparent animate-spin"></div>
          <div class="absolute inset-0 flex items-center justify-center text-fintech-emerald text-xl">
            <i class="fas fa-brain animate-pulse"></i>
          </div>
        </div>
        <h3 class="text-xl font-bold text-white mb-2">${state.loadingMessage}</h3>
        <p class="text-xs text-fintech-textMuted mb-4">${state.loadingSubtext}</p>
        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden p-0.5 border border-slate-700">
          <div class="bg-gradient-to-r from-indigo-500 to-fintech-emerald h-full rounded-full w-3/4 animate-pulse"></div>
        </div>
      </div>
    `;
  }
}
