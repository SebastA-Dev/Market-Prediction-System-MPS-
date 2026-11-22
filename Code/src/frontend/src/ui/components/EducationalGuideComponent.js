/**
 * Componente: EducationalGuideComponent
 * Página completa y dedicada de educación e inversión cuantitativa (UC-08, RF-41, RF-42).
 * Incluye glosario de métricas, vehículos de inversión, cursos de YouTube y herramientas externas.
 */
export class EducationalGuideComponent {
  constructor() {
    this.currentFilterCategory = 'all';
    this.searchQuery = '';
  }

  render(state) {
    if (state.currentView !== 'guide') return '';

    return `
      <!-- ==================================================================== -->
      <!-- VIEW 2: DEDICATED INVESTMENT GUIDE (GUÍA DE INVERSIÓN PAGINA)       -->
      <!-- ==================================================================== -->
      <div id="guide-view" class="w-full space-y-10 animate-fade-in">
        
        <!-- Header Guía -->
        <div class="glass-card p-6 sm:p-8 rounded-3xl border-l-4 border-l-indigo-500 relative overflow-hidden shadow-2xl">
          <div class="max-w-4xl">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-[11px] font-extrabold uppercase tracking-widest px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 inline-flex items-center gap-1.5">
                <i class="fas fa-book-open"></i> Academia y Recursos Financieros
              </span>
              <span class="text-[11px] font-semibold text-slate-400 hidden sm:inline">• Información directa sin modales</span>
            </div>
            <h1 class="text-3xl sm:text-4xl font-black text-white tracking-tight">
              Guía Completa de <span class="text-gradient-indigo">Inversión Cuantitativa</span>
            </h1>
            <p class="text-slate-300 text-sm mt-3 leading-relaxed max-w-3xl">
              Aprende sin jerga confusa. Aquí encontrarás la explicación detallada de todas las métricas empleadas por el modelo de IA de NexGen Quant, junto con enlaces directos a videos educativos de YouTube y herramientas de análisis financiero internacional.
            </p>
            
            <!-- Quick Jump Links -->
            <div class="flex flex-wrap items-center gap-2 mt-5 pt-4 border-t border-slate-800 text-xs">
              <span class="text-slate-400 font-bold mr-1">Ir rápidamente a:</span>
              <a href="#section-guide-metrics" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-all font-semibold flex items-center gap-1.5">
                <i class="fas fa-calculator text-[10px]"></i> Métricas Financieras
              </a>
              <a href="#section-guide-assets" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 transition-all font-semibold flex items-center gap-1.5">
                <i class="fas fa-layer-group text-[10px]"></i> Tipos de Activos
              </a>
              <a href="#section-guide-youtube" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-red-600/30 text-red-300 border border-red-500/30 transition-all font-semibold flex items-center gap-1.5">
                <i class="fab fa-youtube text-[10px] text-red-400"></i> Videos de YouTube
              </a>
              <a href="#section-guide-tools" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 transition-all font-semibold flex items-center gap-1.5">
                <i class="fas fa-globe text-[10px] text-cyan-400"></i> Herramientas Web
              </a>
            </div>
          </div>
        </div>

        <!-- Buscador Dinámico de Conceptos -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 glass-panel p-4 rounded-2xl border border-slate-800">
          <div class="w-full sm:w-96 glass-card rounded-xl px-4 py-2.5 flex items-center gap-3 border border-slate-700/80">
            <i class="fas fa-search text-indigo-400 text-sm"></i>
            <input type="text" id="guide-search-input" placeholder="Buscar término o video (ej. Dividendo, FCF, Sharpe, VOO)..." class="bg-transparent border-none outline-none text-white text-xs w-full placeholder-slate-500 font-medium">
          </div>

          <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto" id="guide-category-filters">
            <button class="guide-cat-btn px-3.5 py-2 rounded-xl bg-indigo-600 text-white text-xs font-bold transition-all cursor-pointer" data-category="all">Todos</button>
            <button class="guide-cat-btn px-3.5 py-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800 text-xs font-semibold transition-all cursor-pointer" data-category="metricas">Métricas</button>
            <button class="guide-cat-btn px-3.5 py-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800 text-xs font-semibold transition-all cursor-pointer" data-category="activos">Activos</button>
            <button class="guide-cat-btn px-3.5 py-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800 text-xs font-semibold transition-all cursor-pointer" data-category="youtube">YouTube</button>
            <button class="guide-cat-btn px-3.5 py-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800 text-xs font-semibold transition-all cursor-pointer" data-category="herramientas">Herramientas Web</button>
          </div>
        </div>

        <!-- SECCIÓN 1: MÉTRICAS FINANCIERAS CLAVE -->
        <div id="section-guide-metrics" class="space-y-4">
          <div class="flex items-center gap-2 border-b border-slate-800 pb-3">
            <div class="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm">
              <i class="fas fa-calculator"></i>
            </div>
            <div>
              <h2 class="text-xl font-bold text-white">Métricas Financieras Fundamentales</h2>
              <p class="text-xs text-slate-400">Los indicadores clave que la IA evalúa antes de calificar una compra.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <!-- Metric 1: Dividend Yield -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-emerald-500 flex flex-col justify-between" data-category="metricas" data-keywords="dividend yield dividendo rendimiento flujo directo efectivo schd">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px] uppercase tracking-wider">Flujo de Caja Pasivo</span>
                  <i class="fas fa-hand-holding-dollar text-emerald-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">Dividend Yield (Rendimiento por Dividendo)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Porcentaje anual del precio de la acción que la empresa te transfiere en dinero en efectivo directamente a tu cuenta de broker.
                </p>
                <div class="p-3 bg-slate-950/90 rounded-xl border border-slate-800/90 text-[11px] font-mono text-emerald-300 mb-4">
                  Fórmula: (Dividendo Anual USD / Precio de Acción) × 100
                </div>
                <div class="space-y-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
                  <strong class="text-emerald-400 block font-semibold">¿Por qué lo usa la IA?</strong>
                  <p class="text-[11px] leading-tight text-slate-300">Empresas con dividendos constantes y crecientes (ej. SCHD, Apple) proveen un piso de amortiguación durante caídas del mercado.</p>
                </div>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Ejemplo Real:</strong> Si compras SCHD a $80 y paga $2.76 al año, su Dividend Yield es <strong>3.45%</strong>.
              </div>
            </div>

            <!-- Metric 2: FCF Yield -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-indigo-500 flex flex-col justify-between" data-category="metricas" data-keywords="fcf yield free cash flow flujo libre caja efectivo meta aapl">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-indigo-500/20 text-indigo-400 font-bold text-[10px] uppercase tracking-wider">Salud Financiera Real</span>
                  <i class="fas fa-piggy-bank text-indigo-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">FCF Yield (Free Cash Flow Yield)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Mide el porcentaje de dinero sobrante en efectivo real que produce la compañía tras cubrir todos sus costos de operación e infraestructura.
                </p>
                <div class="p-3 bg-slate-950/90 rounded-xl border border-slate-800/90 text-[11px] font-mono text-indigo-300 mb-4">
                  Fórmula: (Flujo de Caja Libre / Market Cap) × 100
                </div>
                <div class="space-y-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
                  <strong class="text-indigo-300 block font-semibold">Regla del Modelo Cuantitativo:</strong>
                  <p class="text-[11px] leading-tight text-slate-300">Un FCF Yield &gt; 4% indica que la empresa es una "máquina de imprimir dinero" y no depende de deuda cara para sobrevivir.</p>
                </div>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Ejemplo Real:</strong> Meta Platforms (META) ostenta un FCF Yield ~4.8%, permitiéndole invertir billones en IA.
              </div>
            </div>

            <!-- Metric 3: Ratio Sharpe -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-amber-500 flex flex-col justify-between" data-category="metricas" data-keywords="ratio sharpe riesgo retorno eficiencia monte carlo volatilidad">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-amber-500/20 text-amber-400 font-bold text-[10px] uppercase tracking-wider">Eficiencia de Riesgo</span>
                  <i class="fas fa-scale-balanced text-amber-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">Ratio de Sharpe (Eficiencia)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Cuantifica la ganancia adicional que genera la estrategia por cada unidad de volatilidad o riesgo de pérdida asumido.
                </p>
                <div class="p-3 bg-slate-950/90 rounded-xl border border-slate-800/90 text-[11px] font-mono text-amber-300 mb-4">
                  Sharpe &lt; 1.0: Pobre | Sharpe &gt; 1.5: Excelente
                </div>
                <div class="space-y-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
                  <strong class="text-amber-400 block font-semibold">Criterio de Evaluación:</strong>
                  <p class="text-[11px] leading-tight text-slate-300">Un retorno del 30% no sirve si se logra arriesgando perder el 60% de tu dinero. El Sharpe asegura el equilibrio.</p>
                </div>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Portafolio All-Weather:</strong> Mantiene un Ratio de Sharpe de <strong>1.85</strong> frente a 0.95 del S&P 500 concentrado.
              </div>
            </div>

            <!-- Metric 4: PER (P/E Ratio) -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-purple-500 flex flex-col justify-between" data-category="metricas" data-keywords="pe ratio per precio ganancias valuacion multiplicador nvda">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-purple-500/20 text-purple-400 font-bold text-[10px] uppercase tracking-wider">Valuación de Mercado</span>
                  <i class="fas fa-chart-line text-purple-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">Ratio P/E o PER (Price-to-Earnings)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Indica cuántos dólares pagan los inversores por cada $1 dólar de beneficio neto generado por la empresa.
                </p>
                <div class="p-3 bg-slate-950/90 rounded-xl border border-slate-800/90 text-[11px] font-mono text-purple-300 mb-4">
                  Fórmula: Precio por Acción / Ganancia por Acción (EPS)
                </div>
                <div class="space-y-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
                  <strong class="text-purple-300 block font-semibold">Interpretación:</strong>
                  <p class="text-[11px] leading-tight text-slate-300">Un PER de 25x significa que se pagan 25 años de ganancias actuales. En tecnológicas con alto crecimiento, PERs más altos están justificados.</p>
                </div>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Comparativa:</strong> Promedio histórico S&P 500 = 18x | Sector Tech = 28x-35x.
              </div>
            </div>

            <!-- Metric 5: Beta & Volatilidad -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-cyan-500 flex flex-col justify-between" data-category="metricas" data-keywords="beta volatilidad riesgo oscilacion smh tech">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-cyan-500/20 text-cyan-400 font-bold text-[10px] uppercase tracking-wider">Sensibilidad</span>
                  <i class="fas fa-wave-square text-cyan-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">Beta (Sensibilidad de Mercado)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Mide cuánto reacciona el precio de un activo frente a las oscilaciones del índice general (S&P 500 con Beta = 1.0).
                </p>
                <div class="p-3 bg-slate-950/90 rounded-xl border border-slate-800/90 text-[11px] font-mono text-cyan-300 mb-4">
                  Beta &gt; 1.0: Más volátil | Beta &lt; 1.0: Más estable
                </div>
                <div class="space-y-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
                  <strong class="text-cyan-300 block font-semibold">Aplicación Práctica:</strong>
                  <p class="text-[11px] leading-tight text-slate-300">Si el ETF de semiconductores (SMH) tiene Beta 1.4, cuando el S&P 500 sube 10%, SMH tiende a subir 14% (y viceversa).</p>
                </div>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Protección:</strong> Asignar renta fija o billetes T-Bill (Beta ~0.0) neutraliza las caídas.
              </div>
            </div>

            <!-- Metric 6: Max Drawdown -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-rose-500 flex flex-col justify-between" data-category="metricas" data-keywords="max drawdown caida maxima freno stop loss proteccion">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-rose-500/20 text-rose-400 font-bold text-[10px] uppercase tracking-wider">Control de Pérdida</span>
                  <i class="fas fa-arrow-trend-down text-rose-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">Máximo Desplome (Max Drawdown)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  La mayor pérdida porcentual registrada desde el pico más alto del portafolio hasta su punto más bajo en un período determinado.
                </p>
                <div class="p-3 bg-slate-950/90 rounded-xl border border-slate-800/90 text-[11px] font-mono text-rose-300 mb-4">
                  Objetivo IA: Limitar Drawdown a &lt; -12%
                </div>
                <div class="space-y-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-4">
                  <strong class="text-rose-400 block font-semibold">Por qué es Vital:</strong>
                  <p class="text-[11px] leading-tight text-slate-300">Una caída del 50% requiere un alza del 100% para volver al punto de partida. Evitar grandes desplomes preserva la magia del interés compuesto.</p>
                </div>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Regla de Oro:</strong> Usar Stop-Loss preventivo en un -10% sobre posiciones de alta beta.
              </div>
            </div>

          </div>
        </div>

        <!-- SECCIÓN 2: TIPOS DE ACTIVOS -->
        <div id="section-guide-assets" class="space-y-4 pt-4">
          <div class="flex items-center gap-2 border-b border-slate-800 pb-3">
            <div class="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">
              <i class="fas fa-layer-group"></i>
            </div>
            <div>
              <h2 class="text-xl font-bold text-white">Vehículos de Inversión Sugeridos</h2>
              <p class="text-xs text-slate-400">Instrumentos financieros recomendados en los planes de compra de NexGen Quant.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <!-- Asset 1: ETFs -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-blue-500 flex flex-col justify-between" data-category="activos" data-keywords="etf fondos cotizados voo schd botz smh diversificacion">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 font-bold text-[10px] uppercase tracking-wider">Cesta de Activos</span>
                  <i class="fas fa-boxes-stacked text-blue-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">ETFs (Exchange Traded Funds)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Fondos cotizados en bolsa que agrupan decenas o cientos de acciones en una sola orden de compra.
                </p>
                <ul class="text-xs text-slate-300 space-y-1.5 list-disc pl-4 mb-4">
                  <li><strong>VOO:</strong> Las 500 mayores empresas de EE.UU.</li>
                  <li><strong>SCHD:</strong> Cesta de empresas con dividendos crecientes.</li>
                  <li><strong>SMH:</strong> 25 gigantes globales de semiconductores.</li>
                </ul>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Ventaja:</strong> Otorga diversificación instantánea reduciendo el riesgo de quiebra individual a casi cero.
              </div>
            </div>

            <!-- Asset 2: Acciones Directas -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-emerald-500 flex flex-col justify-between" data-category="activos" data-keywords="acciones directas aapl meta nvda fcx crecimiento cash cow">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px] uppercase tracking-wider">Títulos de Propiedad</span>
                  <i class="fas fa-building text-emerald-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">Acciones Directas (Equities)</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Títulos que te convierten en dueño fraccionario de empresas individuales con derecho a dividendos y apreciación de capital.
                </p>
                <ul class="text-xs text-slate-300 space-y-1.5 list-disc pl-4 mb-4">
                  <li><strong>Cash Cows (Apple/Meta):</strong> Empresas con monopolio y flujo libre de caja positivo.</li>
                  <li><strong>Puras IA (NVIDIA):</strong> Motores de rendimiento acelerado.</li>
                </ul>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Estrategia:</strong> Representan entre el 30% y 40% del presupuesto para capturar alpha (sobreganancia).
              </div>
            </div>

            <!-- Asset 3: Commodities & Cash -->
            <div class="guide-card glass-card p-6 rounded-2xl border-l-4 border-l-amber-500 flex flex-col justify-between" data-category="activos" data-keywords="oro materias primas gld bil t-bills refugio cobertura inflacion">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="px-2.5 py-1 rounded bg-amber-500/20 text-amber-400 font-bold text-[10px] uppercase tracking-wider">Protección Anti-Crisis</span>
                  <i class="fas fa-coins text-amber-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-black text-white mb-2">Commodities, Oro y T-Bills</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Activos descorrelacionados del mercado accionario diseñados para resistir shocks geopolíticos e hiperinflación.
                </p>
                <ul class="text-xs text-slate-300 space-y-1.5 list-disc pl-4 mb-4">
                  <li><strong>GLD (Oro Físico):</strong> Reserva de valor histórica sin riesgo crediticio.</li>
                  <li><strong>BIL (T-Bills):</strong> Deuda del Tesoro EE.UU. a corto plazo acumulando ~5.15% de interés.</li>
                </ul>
              </div>
              <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <strong class="text-white">Rol Cuantitativo:</strong> Se activan cuando la volatilidad azota la tecnología.
              </div>
            </div>

          </div>
        </div>

        <!-- SECCIÓN 3: BIBLIOTECA DE VIDEOS RECOMENDADOS EN YOUTUBE -->
        <div id="section-guide-youtube" class="space-y-4 pt-4">
          <div class="flex items-center justify-between border-b border-slate-800 pb-3">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-xl bg-red-500/20 text-red-400 flex items-center justify-center font-bold text-sm">
                <i class="fab fa-youtube"></i>
              </div>
              <div>
                <h2 class="text-xl font-bold text-white">Biblioteca de Aprendizaje en YouTube</h2>
                <p class="text-xs text-slate-400">Cursos completos y explicaciones en video recomendadas para profundizar.</p>
              </div>
            </div>
            <span class="text-[11px] px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 border border-red-500/20 font-bold hidden sm:inline">
              <i class="fas fa-play mr-1"></i> Acceso Directo Gratuito
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <!-- Video Card 1 -->
            <div class="guide-card glass-card p-5 rounded-2xl border-l-4 border-l-red-500 flex flex-col justify-between hover:bg-slate-900/80 transition-all shadow-xl" data-category="youtube" data-keywords="youtube video curso completo invertir bolsa desde cero andres garza principiantes">
              <div>
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-red-500/20 text-red-400 font-extrabold text-[10px] uppercase tracking-wider flex items-center gap-1">
                    <i class="fab fa-youtube"></i> Curso Completo
                  </span>
                  <span class="text-[10px] font-mono font-bold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">45 Minutos</span>
                </div>

                <h3 class="text-base font-extrabold text-white mb-2 leading-snug">
                  Curso Completo de Inversiones: Cómo Invertir en la Bolsa Desde Cero
                </h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Guía estructurada paso a paso para entender la apertura de cuenta en brokers regulados, compra de acciones fraccionadas y selección de ETFs.
                </p>

                <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-[11px] text-slate-300 space-y-1 mb-4">
                  <div class="font-bold text-slate-200">Canal: Andrés Garza</div>
                  <div class="text-[10px] text-slate-400">Temas: Apertura de Broker, Ordenes Límite/Market, Psicología Inversora.</div>
                </div>
              </div>

              <a href="https://www.youtube.com/watch?v=vt5WfGC_6gE" target="_blank" rel="noopener" class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-all shadow-md">
                <i class="fab fa-youtube text-base"></i> Ver Video en YouTube <i class="fas fa-external-link-alt text-[10px]"></i>
              </a>
            </div>

            <!-- Video Card 2 -->
            <div class="guide-card glass-card p-5 rounded-2xl border-l-4 border-l-red-500 flex flex-col justify-between hover:bg-slate-900/80 transition-all shadow-xl" data-category="youtube" data-keywords="youtube video etf voo schd principiantes winston cordero 3 etfs">
              <div>
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-red-500/20 text-red-400 font-extrabold text-[10px] uppercase tracking-wider flex items-center gap-1">
                    <i class="fab fa-youtube"></i> Selección de ETFs
                  </span>
                  <span class="text-[10px] font-mono font-bold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">17 Minutos</span>
                </div>

                <h3 class="text-base font-extrabold text-white mb-2 leading-snug">
                  Los Únicos 3 ETFs que Necesitas para Hacer Dinero (Como Principiante)
                </h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Análisis práctico de los ETFs más eficientes del mercado global (S&P 500, Dividendos Crecientes y Tecnología) para construir riqueza pasiva.
                </p>

                <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-[11px] text-slate-300 space-y-1 mb-4">
                  <div class="font-bold text-slate-200">Canal: Winston Cordero</div>
                  <div class="text-[10px] text-slate-400">Temas: Indexación pasiva, SCHD vs VOO, comisiones TER.</div>
                </div>
              </div>

              <a href="https://www.youtube.com/watch?v=EBaVujg_Okw" target="_blank" rel="noopener" class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-all shadow-md">
                <i class="fab fa-youtube text-base"></i> Ver Video en YouTube <i class="fas fa-external-link-alt text-[10px]"></i>
              </a>
            </div>

            <!-- Video Card 3 -->
            <div class="guide-card glass-card p-5 rounded-2xl border-l-4 border-l-red-500 flex flex-col justify-between hover:bg-slate-900/80 transition-all shadow-xl" data-category="youtube" data-keywords="youtube video dividendos schd voo coke dividendos rendimiento">
              <div>
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-red-500/20 text-red-400 font-extrabold text-[10px] uppercase tracking-wider flex items-center gap-1">
                    <i class="fab fa-youtube"></i> Estrategia Dividendos
                  </span>
                  <span class="text-[10px] font-mono font-bold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">11 Minutos</span>
                </div>

                <h3 class="text-base font-extrabold text-white mb-2 leading-snug">
                  SCHD vs VOO: Dividendos Crecientes vs Crecimiento S&P 500
                </h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Comparativa directa con números reales simulando un portafolio de $50,000 USD invertidos en rendimiento por dividendo versus revalorización pura.
                </p>

                <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-[11px] text-slate-300 space-y-1 mb-4">
                  <div class="font-bold text-slate-200">Canal: Coke Dividendos</div>
                  <div class="text-[10px] text-slate-400">Temas: Flujo de caja, interés compuesto, rebalanceo.</div>
                </div>
              </div>

              <a href="https://www.youtube.com/watch?v=By6SToD1gHE" target="_blank" rel="noopener" class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-all shadow-md">
                <i class="fab fa-youtube text-base"></i> Ver Video en YouTube <i class="fas fa-external-link-alt text-[10px]"></i>
              </a>
            </div>

            <!-- Video Card 4 -->
            <div class="guide-card glass-card p-5 rounded-2xl border-l-4 border-l-red-500 flex flex-col justify-between hover:bg-slate-900/80 transition-all shadow-xl" data-category="youtube" data-keywords="youtube video cesar dabian finanzas basico fundamentos">
              <div>
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-red-500/20 text-red-400 font-extrabold text-[10px] uppercase tracking-wider flex items-center gap-1">
                    <i class="fab fa-youtube"></i> Fundamentos Financieros
                  </span>
                  <span class="text-[10px] font-mono font-bold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">26 Minutos</span>
                </div>

                <h3 class="text-base font-extrabold text-white mb-2 leading-snug">
                  Aprende a Invertir Desde Cero: Nivel Básico e Intermedio
                </h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Conceptos esenciales sobre tasas de interés, inflación, diversificación por sectores y cómo evitar estafas financieras comunes.
                </p>

                <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-[11px] text-slate-300 space-y-1 mb-4">
                  <div class="font-bold text-slate-200">Canal: César Dabián Finanzas</div>
                  <div class="text-[10px] text-slate-400">Temas: Gestión de riesgo, perfil conservador/agresivo.</div>
                </div>
              </div>

              <a href="https://www.youtube.com/watch?v=2ibqfxEAESo" target="_blank" rel="noopener" class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-all shadow-md">
                <i class="fab fa-youtube text-base"></i> Ver Video en YouTube <i class="fas fa-external-link-alt text-[10px]"></i>
              </a>
            </div>

          </div>
        </div>

        <!-- SECCIÓN 4: HERRAMIENTAS Y SITIOS WEB FINANCIEROS RECOMENDADOS -->
        <div id="section-guide-tools" class="space-y-4 pt-4">
          <div class="flex items-center gap-2 border-b border-slate-800 pb-3">
            <div class="w-8 h-8 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-sm">
              <i class="fas fa-globe"></i>
            </div>
            <div>
              <h2 class="text-xl font-bold text-white">Herramientas Web y Plataformas Institucionales</h2>
              <p class="text-xs text-slate-400">Sitios externos recomendados para auditar datos, simulaciones y reportes oficiales.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

            <!-- Tool 1: Portfolio Visualizer -->
            <div class="guide-card glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/50 flex flex-col justify-between transition-all" data-category="herramientas" data-keywords="herramientas web portfolio visualizer monte carlo backtesting simuacion">
              <div>
                <div class="flex justify-between items-start mb-2">
                  <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-bold">Simulación & Backtest</span>
                  <i class="fas fa-chart-pie text-cyan-400"></i>
                </div>
                <h3 class="text-base font-bold text-white mb-1">Portfolio Visualizer</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Herramienta online gratuita para realizar simulaciones Monte Carlo, comprobar rendimientos históricos y analizar la correlación entre activos desde 1985.
                </p>
              </div>
              <a href="https://www.portfoliovisualizer.com" target="_blank" rel="noopener" class="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-slate-700 hover:border-cyan-500/50 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all">
                <span>Visitar Website</span> <i class="fas fa-arrow-up-right-from-square text-[10px]"></i>
              </a>
            </div>

            <!-- Tool 2: Seeking Alpha -->
            <div class="guide-card glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/50 flex flex-col justify-between transition-all" data-category="herramientas" data-keywords="herramientas web seeking alpha metricas dividendos fcf reportes">
              <div>
                <div class="flex justify-between items-start mb-2">
                  <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-bold">Análisis Fundamental</span>
                  <i class="fas fa-magnifying-glass-chart text-cyan-400"></i>
                </div>
                <h3 class="text-base font-bold text-white mb-1">Seeking Alpha</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Plataforma de consulta de métricas detalladas de Free Cash Flow, historial de pago de dividendos y transcripciones de llamadas de resultados de empresas globales.
                </p>
              </div>
              <a href="https://seekingalpha.com" target="_blank" rel="noopener" class="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-slate-700 hover:border-cyan-500/50 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all">
                <span>Visitar Website</span> <i class="fas fa-arrow-up-right-from-square text-[10px]"></i>
              </a>
            </div>

            <!-- Tool 3: SEC EDGAR -->
            <div class="guide-card glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/50 flex flex-col justify-between transition-all" data-category="herramientas" data-keywords="herramientas web sec edgar reportes oficiales 10k 10q estados financieros">
              <div>
                <div class="flex justify-between items-start mb-2">
                  <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-bold">Oficial EE.UU.</span>
                  <i class="fas fa-landmark text-cyan-400"></i>
                </div>
                <h3 class="text-base font-bold text-white mb-1">SEC EDGAR System</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Registro oficial del gobierno de EE.UU. donde cada empresa cotizada presenta sus reportes auditos 10-K (Anual) y 10-Q (Trimestral) sin intermediarios.
                </p>
              </div>
              <a href="https://www.sec.gov/edgar" target="_blank" rel="noopener" class="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-slate-700 hover:border-cyan-500/50 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all">
                <span>Visitar Website</span> <i class="fas fa-arrow-up-right-from-square text-[10px]"></i>
              </a>
            </div>

            <!-- Tool 4: Investopedia -->
            <div class="guide-card glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/50 flex flex-col justify-between transition-all" data-category="herramientas" data-keywords="herramientas web investopedia enciclopedia conceptos diccionario">
              <div>
                <div class="flex justify-between items-start mb-2">
                  <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-bold">Enciclopedia Financiera</span>
                  <i class="fas fa-graduation-cap text-cyan-400"></i>
                </div>
                <h3 class="text-base font-bold text-white mb-1">Investopedia</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  La mayor biblioteca educativa del mundo sobre terminología, fórmulas de finanzas corporativas, gestión de patrimonio y derivados.
                </p>
              </div>
              <a href="https://www.investopedia.com" target="_blank" rel="noopener" class="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-slate-700 hover:border-cyan-500/50 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all">
                <span>Visitar Website</span> <i class="fas fa-arrow-up-right-from-square text-[10px]"></i>
              </a>
            </div>

            <!-- Tool 5: Yahoo Finance & TradingView -->
            <div class="guide-card glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/50 flex flex-col justify-between transition-all" data-category="herramientas" data-keywords="herramientas web yahoo finance tradingview cotizaciones graficos tiempo real">
              <div>
                <div class="flex justify-between items-start mb-2">
                  <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-bold">Mercado en Tiempo Real</span>
                  <i class="fas fa-chart-line text-cyan-400"></i>
                </div>
                <h3 class="text-base font-bold text-white mb-1">Yahoo Finance & TradingView</h3>
                <p class="text-xs text-slate-300 leading-relaxed mb-4">
                  Herramientas esenciales para el seguimiento diario de cotizaciones de acciones, precios de commodities y noticias macroeconómicas de última hora.
                </p>
              </div>
              <a href="https://finance.yahoo.com" target="_blank" rel="noopener" class="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-slate-700 hover:border-cyan-500/50 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all">
                <span>Visitar Website</span> <i class="fas fa-arrow-up-right-from-square text-[10px]"></i>
              </a>
            </div>

          </div>
        </div>

      </div>
    `;
  }

  attachEvents(container) {
    const searchInput = container.querySelector('#guide-search-input');
    const catBtns = container.querySelectorAll('.guide-cat-btn');
    const cards = container.querySelectorAll('.guide-card');

    const filterCards = () => {
      const q = (searchInput?.value || '').toLowerCase().trim();
      const cat = this.currentFilterCategory;

      cards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        const keywords = card.getAttribute('data-keywords') || '';
        const text = card.innerText.toLowerCase();

        const matchesCat = (cat === 'all' || cardCat === cat);
        const matchesQuery = (!q || text.includes(q) || keywords.includes(q));

        if (matchesCat && matchesQuery) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    };

    if (searchInput) {
      searchInput.onkeyup = filterCards;
    }

    catBtns.forEach(btn => {
      btn.onclick = () => {
        catBtns.forEach(b => {
          b.className = 'guide-cat-btn px-3.5 py-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800 text-xs font-semibold transition-all cursor-pointer';
        });
        btn.className = 'guide-cat-btn px-3.5 py-2 rounded-xl bg-indigo-600 text-white text-xs font-bold transition-all cursor-pointer';

        this.currentFilterCategory = btn.getAttribute('data-category') || 'all';
        filterCards();
      };
    });
  }
}
