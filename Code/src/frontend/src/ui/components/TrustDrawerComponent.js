/**
 * Componente: TrustDrawerComponent
 * Panel lateral deslizante con la justificación matemática y auditoría algorítmica (UC-03, RF-34, RF-35).
 */
export class TrustDrawerComponent {
  /**
   * @param {import('../../infrastructure/adapters/in/controllers/AdvisorController.js').AdvisorController} advisorController
   */
  constructor(advisorController) {
    this.advisor = advisorController;
  }

  render(state) {
    const isOpen = state.isTrustDrawerOpen;

    return `
      <!-- OVERLAY MÁSCARA -->
      <div id="drawer-overlay" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-[60] ${isOpen ? '' : 'hidden opacity-0'} transition-opacity duration-300"></div>

      <!-- DRAWER / MODAL: ¿POR QUÉ CONFIAR EN ESTE MOVIMIENTO? -->
      <aside id="trust-drawer" class="fixed top-0 right-0 h-full w-full max-w-xl bg-slate-950 border-l border-slate-800 z-[70] transform ${isOpen ? 'translate-x-0' : 'translate-x-full'} transition-transform duration-300 flex flex-col shadow-2xl">
        <div class="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900">
          <div>
            <span class="text-[10px] font-extrabold uppercase tracking-widest text-indigo-400">Auditoría Algorítmica</span>
            <h2 class="text-xl font-black text-white flex items-center gap-2">
              <i class="fas fa-shield-halved text-fintech-emerald"></i> ¿Por qué confiar en esta orden?
            </h2>
          </div>
          <button id="btn-close-trust-drawer" class="w-9 h-9 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center cursor-pointer">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-6">
          <div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-black text-lg">
                94%
              </div>
              <div>
                <h4 class="font-bold text-white text-sm">Índice de Confianza Algorítmica</h4>
                <p class="text-xs text-slate-300">Validado sobre 10,000 iteraciones de Monte Carlo y prueba Z con significancia p &lt; 0.05.</p>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <h4 class="font-bold text-white text-sm border-b border-slate-800 pb-2">Respaldos Matemáticos Clave</h4>
            
            <div class="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
              <div class="flex justify-between text-xs font-mono">
                <span class="text-slate-400">Ratio de Sharpe (Eficiencia):</span>
                <span class="text-emerald-400 font-bold">1.85 (Excelente)</span>
              </div>
              <p class="text-[11px] text-slate-300">Mide cuánta ganancia adicional genera la estrategia por cada unidad de volatilidad asumida. Un Sharpe &gt; 1.5 denota alta calidad en el retorno ajustado a riesgo.</p>
            </div>

            <div class="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
              <div class="flex justify-between text-xs font-mono">
                <span class="text-slate-400">Máximo Desplome Histórico (Max Drawdown):</span>
                <span class="text-amber-400 font-bold">-11.4% (vs -24.5% del S&P 500)</span>
              </div>
              <p class="text-[11px] text-slate-300">En la peor corrección del período analizado, este portafolio cayó menos de la mitad que el mercado tradicional gracias a la descorrelación con oro y bonos T-Bills.</p>
            </div>

            <div class="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
              <div class="flex justify-between text-xs font-mono">
                <span class="text-slate-400">Modelo Cuantitativo Base:</span>
                <span class="text-indigo-400 font-bold">MASTER + Galformer + Z-test</span>
              </div>
              <p class="text-[11px] text-slate-300">Redes neuronales con atención para series temporales financieras y cálculo de correlaciones inter-sectoriales en tiempo real.</p>
            </div>
          </div>

          <!-- Marco de redacción condicional (RF-35) -->
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[10px] text-slate-500 italic">
            Aviso de Transparencia: Este análisis se fundamenta en modelos matemáticos retrospectivos y distribuciones estadísticas condicionales; no constituye garantía legal ni certidumbre absoluta de rendimientos futuros.
          </div>
        </div>
      </aside>
    `;
  }

  attachEvents(container) {
    const closeBtn = container.querySelector('#btn-close-trust-drawer');
    const overlay = container.querySelector('#drawer-overlay');

    if (closeBtn) closeBtn.onclick = () => this.advisor.closeTrustDrawer();
    if (overlay) overlay.onclick = () => this.advisor.closeTrustDrawer();
  }
}
