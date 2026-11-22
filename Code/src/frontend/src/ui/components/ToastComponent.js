/**
 * Componente: ToastComponent
 * Contenedor de notificaciones flotantes en tiempo real.
 */
export class ToastComponent {
  render(state) {
    const toasts = state.toasts || [];
    if (toasts.length === 0) return `<div id="toast-container" class="fixed bottom-6 right-6 z-[90] space-y-2 pointer-events-none"></div>`;

    return `
      <div id="toast-container" class="fixed bottom-6 right-6 z-[90] space-y-2 pointer-events-none">
        ${toasts.map(t => `
          <div class="p-3.5 rounded-xl glass-card text-xs text-white border ${
            t.type === 'success' ? 'border-emerald-500/50 text-emerald-300' : 'border-indigo-500/50 text-indigo-300'
          } shadow-2xl flex items-center gap-2 animate-slide-up pointer-events-auto">
            <i class="fas ${t.type === 'success' ? 'fa-circle-check text-emerald-400' : 'fa-circle-info text-indigo-400'}"></i>
            <span>${t.message}</span>
          </div>
        `).join('')}
      </div>
    `;
  }
}
