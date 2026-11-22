/**
 * Componente: SearchPromptComponent
 * Sección de entrada de intención conversacional (UC-01, RF-30 a RF-33).
 */
export class SearchPromptComponent {
  /**
   * @param {import('../../infrastructure/adapters/in/controllers/AdvisorController.js').AdvisorController} advisorController
   */
  constructor(advisorController) {
    this.advisor = advisorController;
  }

  render(state) {
    const hasResults = Boolean(state.predictionIntent);

    return `
      <div class="w-full max-w-3xl ${hasResults ? 'mb-4' : 'mb-8'} flex flex-col items-center animate-fade-in" id="search-container">
        
        <div class="text-center mb-6" id="main-title-container">
          <span class="text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-3 inline-block">
            <i class="fas fa-robot mr-1"></i> Consejero Financiero Cuantitativo
          </span>
          <h1 class="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight mt-1" id="main-title">
            ¿Qué movimiento deseas <span class="text-gradient-emerald">ejecutar hoy?</span>
          </h1>
          <p class="text-sm text-slate-400 mt-2 max-w-xl mx-auto" id="main-subtitle">
            Ingresa tu monto de inversión o sector objetivo. Obtendrás un plan de compra exacto, con montos por activo, puntos de entrada y capacidad de explorar cada sector hasta el nivel de empresa.
          </p>
        </div>
        
        <!-- Dynamic Prompt Input -->
        <div class="w-full relative glass-card rounded-2xl p-2.5 transition-all focus-within:border-fintech-emerald focus-within:ring-2 focus-within:ring-fintech-emerald/20 flex flex-col sm:flex-row items-center gap-2 shadow-fintech-card">
          <div class="hidden sm:flex items-center pl-3 text-fintech-emerald">
            <i class="fas fa-coins text-xl"></i>
          </div>
          <input 
            id="prompt-input" 
            type="text" 
            class="w-full bg-transparent border-none outline-none text-white px-3 py-3 text-base sm:text-lg placeholder-slate-500 font-medium" 
            placeholder="Ej: Deseo invertir $20,000 a mediano plazo..."
            value="${state.predictionIntent?.rawPrompt || ''}"
          />
          <button 
            id="btn-generate-plan" 
            class="w-full sm:w-auto px-7 py-3.5 bg-gradient-to-r from-fintech-emerald to-emerald-600 hover:from-emerald-400 hover:to-fintech-emerald text-slate-950 font-extrabold rounded-xl transition-all shadow-glow-emerald shrink-0 flex items-center justify-center gap-2 text-sm tracking-wide cursor-pointer"
          >
            <span>Generar Plan</span> <i class="fas fa-arrow-right text-xs"></i>
          </button>
        </div>

        <!-- Sugerencias de Clic Rápido -->
        <div id="suggestions" class="${hasResults ? 'hidden' : ''} mt-5 w-full">
          <p class="text-[11px] text-slate-400 uppercase tracking-wider font-bold mb-2.5 text-center">Consultas de alto impacto recomendadas:</p>
          <div class="flex flex-wrap justify-center gap-2">
            <button class="suggestion-chip text-xs px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 text-slate-300 transition-all flex items-center gap-2 hover:border-emerald-500/50 cursor-pointer" data-prompt="Deseo invertir 20000 a mediano plazo">
              <i class="fas fa-vault text-emerald-400 text-xs"></i> "Invertir $20,000 a mediano plazo"
            </button>
            <button class="suggestion-chip text-xs px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 text-slate-300 transition-all flex items-center gap-2 hover:border-indigo-500/50 cursor-pointer" data-prompt="Deseo invertir 7000 en el sector tecnologico">
              <i class="fas fa-laptop-code text-indigo-400 text-xs"></i> "Invertir $7,000 en tecnología"
            </button>
            <button class="suggestion-chip text-xs px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 text-slate-300 transition-all flex items-center gap-2 hover:border-cyan-500/50 cursor-pointer" data-prompt="Deseo invertir 3000 en Semiconductores">
              <i class="fas fa-microchip text-cyan-400 text-xs"></i> "Invertir $3,000 en Semiconductores"
            </button>
          </div>
        </div>

      </div>
    `;
  }

  attachEvents(container) {
    const input = container.querySelector('#prompt-input');
    const submitBtn = container.querySelector('#btn-generate-plan');

    const handleSend = () => {
      const text = input ? input.value : '';
      this.advisor.submitPrompt(text);
    };

    if (submitBtn) {
      submitBtn.onclick = handleSend;
    }

    if (input) {
      input.onkeypress = (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleSend();
        }
      };
    }

    const chips = container.querySelectorAll('.suggestion-chip');
    chips.forEach(chip => {
      chip.onclick = () => {
        const prompt = chip.getAttribute('data-prompt');
        if (input) input.value = prompt;
        this.advisor.submitPrompt(prompt);
      };
    });
  }
}
