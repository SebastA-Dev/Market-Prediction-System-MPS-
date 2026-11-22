import { chartManager } from '../charts/ChartManager.js';

/**
 * Componente: ResultsComponent
 * Renderiza los planes de inversión, desglose macro, micro-sector y nicho (UC-02, UC-04, UC-05, UC-07).
 */
export class ResultsComponent {
  /**
   * @param {import('../../infrastructure/adapters/in/controllers/AdvisorController.js').AdvisorController} advisorController
   */
  constructor(advisorController) {
    this.advisor = advisorController;
  }

  render(state) {
    if (state.isLoading) return '';

    if (state.lastError) {
      return `
        <div id="results-container" class="w-full max-w-3xl space-y-6 animate-slide-up">
          <div class="glass-card p-6 sm:p-8 rounded-3xl border-l-4 border-l-rose-500 shadow-2xl">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center text-xl shrink-0">
                <i class="fas fa-triangle-exclamation"></i>
              </div>
              <div class="flex-1">
                <h3 class="text-xl font-bold text-white mb-2">No se pudo generar la recomendación</h3>
                <p class="text-sm text-slate-300 leading-relaxed mb-4">${state.lastError}</p>
                <div class="flex gap-3">
                  <button id="btn-retry-prompt" class="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs rounded-xl border border-slate-700 flex items-center gap-2 transition-all cursor-pointer">
                    <i class="fas fa-rotate-right"></i> Reintentar consulta
                  </button>
                  <button id="btn-use-fallback" class="px-5 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-bold text-xs rounded-xl border border-emerald-500/30 flex items-center gap-2 transition-all cursor-pointer">
                    <i class="fas fa-eye"></i> Ver simulación basal
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    if (!state.predictionIntent) return '';

    const intent = state.predictionIntent;
    const amountStr = intent.formattedTotalAmount;
    const amountNum = intent.requestedAmount;

    // Si hay un sector activo seleccionado por el usuario (Drill-down a Micro)
    if (state.activeSector) {
      return this._renderMicroView(state, state.activeSector, amountNum, amountStr);
    }

    // Si es un nicho especializado (Semiconductores / Activo individual)
    if (intent.isAsset || intent.rawPrompt.toLowerCase().includes('semiconductores') || intent.rawPrompt.toLowerCase().includes('nvidia')) {
      return this._renderNicheView(state, intent, amountStr, amountNum);
    }

    // Vista Principal: Macro All-Weather
    return this._renderMacroView(state, intent, amountStr, amountNum);
  }

  _renderMacroView(state, intent, amountStr, amountNum) {
    const sp500 = Math.round(amountNum * 0.35);
    const tech = Math.round(amountNum * 0.35);
    const goldComm = Math.round(amountNum * 0.20);
    const cash = Math.round(amountNum * 0.10);

    const format = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

    const isTracked = (ticker) => (state.portfolio || []).some(p => p.ticker.toUpperCase() === ticker.toUpperCase());

    return `
      <div id="results-container" class="w-full space-y-8 animate-slide-up">
        
        <!-- BREADCRUMB HEADER MACRO -->
        <div class="flex items-center justify-between bg-slate-900/60 p-3.5 rounded-2xl border border-slate-800 text-xs">
          <div class="flex items-center gap-2 text-slate-300">
            <span class="text-emerald-400 font-bold"><i class="fas fa-layer-group"></i> Nivel Macro:</span>
            <span>Portafolio General Conservador</span>
            <span class="text-slate-600">•</span>
            <span class="font-mono text-white font-bold">${amountStr}</span>
          </div>
          <span class="text-[11px] text-slate-400 font-medium hidden sm:inline">
            <i class="fas fa-hand-pointer text-emerald-400 mr-1"></i> Haz clic en cualquier sector para explorar empresas exactas
          </span>
        </div>

        <!-- RESUMEN EJECUTIVO MACRO -->
        <div class="glass-card-accent p-6 sm:p-8 rounded-3xl relative overflow-hidden shadow-2xl">
          <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="px-3 py-1 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <i class="fas fa-check-circle"></i> Plan Recomendado Directo
                </span>
                <span class="px-3 py-1 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold text-xs">
                  Horizonte: Mediano Plazo (2-4 años)
                </span>
              </div>
              <h2 class="text-2xl sm:text-4xl font-black text-white tracking-tight">
                Orden Estratégica: <span class="text-gradient-emerald">Portafolio Multiactivo All-Weather</span>
              </h2>
              <p class="text-sm text-slate-300 mt-2 max-w-2xl leading-relaxed">
                Para tu capital de <strong class="text-white font-mono text-base">${amountStr}</strong>, la orden de la IA es distribuir el presupuesto en 4 frentes. **Presiona cualquier tarjeta para ver el desglose exacto de empresas y dividendos.**
              </p>
            </div>
            <div class="flex flex-col sm:flex-row lg:flex-col gap-3 w-full lg:w-auto">
              <button id="btn-open-trust-drawer" class="px-6 py-3.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl border border-slate-700 transition-all flex items-center justify-center gap-2 text-xs uppercase tracking-wider shadow-md hover:border-emerald-500/50 cursor-pointer">
                <i class="fas fa-shield-halved text-fintech-emerald"></i> ¿Por qué confiar en este plan?
              </button>
            </div>
          </div>

          <!-- DESCARGO LEGAL OBLIGATORIO (RF-36) -->
          <div class="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 leading-normal flex items-start gap-2">
            <i class="fas fa-circle-info text-indigo-400 text-xs mt-0.5"></i>
            <span>${intent.confidenceStatement}</span>
          </div>
        </div>

        <!-- CONTEXTO MACROECONÓMICO (RF-37) -->
        ${
          intent.macroContext ? `
            <div class="glass-card p-5 rounded-2xl border-l-4 border-l-indigo-500 text-xs text-slate-300 leading-relaxed">
              <div class="flex items-center gap-2 text-indigo-300 font-bold mb-1 uppercase tracking-wider text-[10px]">
                <i class="fas fa-chart-area"></i> Contexto Macroeconómico Detectado por MASTER
              </div>
              <p>${intent.macroContext}</p>
            </div>
          ` : ''
        }

        <!-- SECTORES INTERACTIVOS CON OPCIÓN DE DRILL-DOWN A MICRO Y BOTÓN GUARDAR -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <i class="fas fa-sitemap text-fintech-emerald"></i> Asignación de Sectores (Haz Clic para Ver Empresas)
            </h3>
            <span class="text-xs text-slate-400 font-mono">Presupuesto total: ${amountStr}</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- SECTOR 1: TECH -->
            <div class="glass-card p-5 rounded-2xl border-l-4 border-l-emerald-500 flex flex-col justify-between clickable-card group relative">
              <div class="sector-card-clickable cursor-pointer" data-sector="tech">
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-extrabold text-[10px] uppercase tracking-wider">35% ASIGNADO</span>
                  <span class="text-xs text-emerald-400 group-hover:translate-x-1 transition-transform"><i class="fas fa-arrow-right"></i></span>
                </div>
                <h4 class="text-lg font-black text-white group-hover:text-emerald-400 transition-colors">Tecnología e IA</h4>
                <p class="text-xs text-slate-300 mt-1">Líderes en Inteligencia Artificial, software y la nube.</p>
              </div>
              <div class="mt-5 pt-4 border-t border-slate-800">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-[10px] uppercase text-slate-400 font-semibold">Monto</span>
                  <span class="text-lg font-black font-mono text-emerald-400">${format(tech)}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 mt-2">
                  <button class="sector-btn-drill py-2 px-2 bg-emerald-500/10 rounded-xl text-emerald-400 font-bold text-[10px] text-center border border-emerald-500/20 hover:bg-emerald-500 hover:text-slate-950 transition-all cursor-pointer" data-sector="tech">
                    <i class="fas fa-microchip mr-1"></i> Empresas
                  </button>
                  <button class="track-btn py-2 px-2 ${isTracked('TECH-SECTOR') ? 'bg-emerald-500 text-slate-950 font-black shadow-glow-emerald border-emerald-400' : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'} rounded-xl font-bold text-[10px] text-center border transition-all cursor-pointer" data-ticker="TECH-SECTOR" data-name="Sector Tecnología e IA" data-amount="${tech}">
                    <i class="fas fa-check mr-1"></i> ${isTracked('TECH-SECTOR') ? 'Invertido' : 'Seguir'}
                  </button>
                </div>
              </div>
            </div>

            <!-- SECTOR 2: S&P 500 -->
            <div class="glass-card p-5 rounded-2xl border-l-4 border-l-blue-500 flex flex-col justify-between clickable-card group relative">
              <div class="sector-card-clickable cursor-pointer" data-sector="sp500">
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 font-extrabold text-[10px] uppercase tracking-wider">35% ASIGNADO</span>
                  <span class="text-xs text-blue-400 group-hover:translate-x-1 transition-transform"><i class="fas fa-arrow-right"></i></span>
                </div>
                <h4 class="text-lg font-black text-white group-hover:text-blue-400 transition-colors">S&P 500 / Ancla EE.UU.</h4>
                <p class="text-xs text-slate-300 mt-1">Indexación diversificada a las 500 corporaciones top.</p>
              </div>
              <div class="mt-5 pt-4 border-t border-slate-800">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-[10px] uppercase text-slate-400 font-semibold">Monto</span>
                  <span class="text-lg font-black font-mono text-blue-400">${format(sp500)}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 mt-2">
                  <button class="sector-btn-drill py-2 px-2 bg-blue-500/10 rounded-xl text-blue-400 font-bold text-[10px] text-center border border-blue-500/20 hover:bg-blue-500 hover:text-slate-950 transition-all cursor-pointer" data-sector="sp500">
                    <i class="fas fa-chart-pie mr-1"></i> ETFs
                  </button>
                  <button class="track-btn py-2 px-2 ${isTracked('VOO') ? 'bg-emerald-500 text-slate-950 font-black shadow-glow-emerald border-emerald-400' : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'} rounded-xl font-bold text-[10px] text-center border transition-all cursor-pointer" data-ticker="VOO" data-name="S&P 500 Indexado" data-amount="${sp500}">
                    <i class="fas fa-check mr-1"></i> ${isTracked('VOO') ? 'Invertido' : 'Seguir'}
                  </button>
                </div>
              </div>
            </div>

            <!-- SECTOR 3: COMMODITIES -->
            <div class="glass-card p-5 rounded-2xl border-l-4 border-l-amber-500 flex flex-col justify-between clickable-card group relative">
              <div class="sector-card-clickable cursor-pointer" data-sector="commodities">
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-amber-500/20 text-amber-400 font-extrabold text-[10px] uppercase tracking-wider">20% ASIGNADO</span>
                  <span class="text-xs text-amber-400 group-hover:translate-x-1 transition-transform"><i class="fas fa-arrow-right"></i></span>
                </div>
                <h4 class="text-lg font-black text-white group-hover:text-amber-400 transition-colors">Materias Primas y Oro</h4>
                <p class="text-xs text-slate-300 mt-1">Cobertura anti-inflación, Cobre, Oro y Energía.</p>
              </div>
              <div class="mt-5 pt-4 border-t border-slate-800">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-[10px] uppercase text-slate-400 font-semibold">Monto</span>
                  <span class="text-lg font-black font-mono text-amber-400">${format(goldComm)}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 mt-2">
                  <button class="sector-btn-drill py-2 px-2 bg-amber-500/10 rounded-xl text-amber-400 font-bold text-[10px] text-center border border-amber-500/20 hover:bg-amber-500 hover:text-slate-950 transition-all cursor-pointer" data-sector="commodities">
                    <i class="fas fa-coins mr-1"></i> Oro/Mineras
                  </button>
                  <button class="track-btn py-2 px-2 ${isTracked('GLD') ? 'bg-emerald-500 text-slate-950 font-black shadow-glow-emerald border-emerald-400' : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'} rounded-xl font-bold text-[10px] text-center border transition-all cursor-pointer" data-ticker="GLD" data-name="SPDR Gold Trust" data-amount="${goldComm}">
                    <i class="fas fa-check mr-1"></i> ${isTracked('GLD') ? 'Invertido' : 'Seguir'}
                  </button>
                </div>
              </div>
            </div>

            <!-- SECTOR 4: LIQUIDEZ Y CASH -->
            <div class="glass-card p-5 rounded-2xl border-l-4 border-l-slate-400 flex flex-col justify-between clickable-card group relative">
              <div class="sector-card-clickable cursor-pointer" data-sector="cash">
                <div class="flex justify-between items-start mb-3">
                  <span class="px-2.5 py-1 rounded bg-slate-500/20 text-slate-300 font-extrabold text-[10px] uppercase tracking-wider">10% ASIGNADO</span>
                  <span class="text-xs text-slate-400 group-hover:translate-x-1 transition-transform"><i class="fas fa-arrow-right"></i></span>
                </div>
                <h4 class="text-lg font-black text-white group-hover:text-slate-300 transition-colors">Liquidez y Renta Fija</h4>
                <p class="text-xs text-slate-300 mt-1">Reserva en dólares al ~5.2% de interés anual.</p>
              </div>
              <div class="mt-5 pt-4 border-t border-slate-800">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-[10px] uppercase text-slate-400 font-semibold">Monto</span>
                  <span class="text-lg font-black font-mono text-slate-200">${format(cash)}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 mt-2">
                  <button class="sector-btn-drill py-2 px-2 bg-slate-500/10 rounded-xl text-slate-300 font-bold text-[10px] text-center border border-slate-500/20 hover:bg-slate-500 hover:text-slate-950 transition-all cursor-pointer" data-sector="cash">
                    <i class="fas fa-vault mr-1"></i> Instrumentos
                  </button>
                  <button class="track-btn py-2 px-2 ${isTracked('BIL') ? 'bg-emerald-500 text-slate-950 font-black shadow-glow-emerald border-emerald-400' : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'} rounded-xl font-bold text-[10px] text-center border transition-all cursor-pointer" data-ticker="BIL" data-name="T-Bills SPDR" data-amount="${cash}">
                    <i class="fas fa-check mr-1"></i> ${isTracked('BIL') ? 'Invertido' : 'Seguir'}
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- PLAN OPERATIVO Y GRÁFICO PROYECCIÓN MONTE CARLO -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
          
          <!-- Plan Operativo -->
          <div class="glass-card p-6 rounded-2xl flex flex-col justify-between">
            <div>
              <h3 class="text-lg font-bold text-white flex items-center gap-2 mb-4">
                <i class="fas fa-route text-fintech-indigo"></i> Plan Operativo de Ejecución (3 Pasos)
              </h3>
              <div class="space-y-4 text-xs">
                <div class="p-3 bg-slate-900 rounded-xl border border-slate-800 flex items-start gap-3">
                  <div class="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 font-bold flex items-center justify-center shrink-0">1</div>
                  <div>
                    <h5 class="font-bold text-white mb-0.5">Selección de Sector</h5>
                    <p class="text-slate-400">Haz clic en cualquiera de las 4 tarjetas superiores para ingresar a la vista micro y obtener las empresas exactas que componen esa partida presupuestaria.</p>
                  </div>
                </div>
                <div class="p-3 bg-slate-900 rounded-xl border border-slate-800 flex items-start gap-3">
                  <div class="w-6 h-6 rounded-lg bg-indigo-500/20 text-indigo-400 font-bold flex items-center justify-center shrink-0">2</div>
                  <div>
                    <h5 class="font-bold text-white mb-0.5">Ejecución en Broker Regulado</h5>
                    <p class="text-slate-400">Ingresa a Interactive Brokers, eToro o tu broker local e introduce las siglas (Tickers) que te indicaremos en cada sección.</p>
                  </div>
                </div>
                <div class="p-3 bg-slate-900 rounded-xl border border-slate-800 flex items-start gap-3">
                  <div class="w-6 h-6 rounded-lg bg-cyan-500/20 text-cyan-400 font-bold flex items-center justify-center shrink-0">3</div>
                  <div>
                    <h5 class="font-bold text-white mb-0.5">Marca tus Posiciones</h5>
                    <p class="text-slate-400">Presiona "Marcar como Invertido" para auditar en tiempo real tus activos guardados desde el menú superior de tu perfil.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Gráfico Simulación Monte Carlo -->
          <div class="glass-card p-6 rounded-2xl flex flex-col justify-between">
            <div>
              <div class="flex justify-between items-center mb-1">
                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                  <i class="fas fa-chart-line text-emerald-400"></i> Simulación Monte Carlo (3 Años)
                </h3>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">+11.2% CAGR</span>
              </div>
              <p class="text-xs text-slate-400 mb-4">Escenario probabilístico de valor de portafolio.</p>
              <div class="relative w-full h-56">
                <canvas id="projectionChart"></canvas>
              </div>
            </div>
            <div class="pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between">
              <span>Basal: +4.0% anual</span>
              <span class="text-emerald-400 font-bold">IA Esperada: +11.2% anual</span>
            </div>
          </div>

        </div>

      </div>
    `;
  }

  _renderMicroView(state, sectorId, amountNum, amountStr) {
    const format = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

    const SECTOR_DATA = {
      tech: {
        title: 'Tecnología e Inteligencia Artificial',
        icon: 'fa-microchip',
        budgetPct: 0.35,
        description: 'Empresas con foso defensivo (moat), monopolios de software y plataformas aceleradas por IA.',
        companies: [
          { ticker: 'AAPL', name: 'Apple Inc.', share: 30, priceEst: 185, div: '0.52%', fcf: '3.8%', pe: '28x', stopLoss: 168, takeProfit: 215, badge: 'Cash Cow', color: 'border-l-emerald-500', text: 'Líder en ecosistema de consumo y hardware premium con recompras masivas.' },
          { ticker: 'META', name: 'Meta Platforms', share: 25, priceEst: 525, div: '0.40%', fcf: '4.8%', pe: '24x', stopLoss: 470, takeProfit: 610, badge: 'Monopolio Social', color: 'border-l-indigo-500', text: 'Monopolio en redes y publicidad digital monetizando modelos abiertos Llama.' },
          { ticker: 'MSFT', name: 'Microsoft Corp', share: 25, priceEst: 420, div: '0.72%', fcf: '3.2%', pe: '33x', stopLoss: 385, takeProfit: 490, badge: 'Nube & Empresa', color: 'border-l-blue-500', text: 'Infraestructura Azure líder corporativa e integración de OpenAI Copilot.' },
          { ticker: 'NVDA', name: 'NVIDIA Corp', share: 20, priceEst: 880, div: '0.08%', fcf: '4.1%', pe: '42x', stopLoss: 790, takeProfit: 1050, badge: 'Acelerador IA', color: 'border-l-amber-500', text: 'Monopolio del 85% en procesadores de cómputo para entrenamiento de LLMs.' }
        ]
      },
      sp500: {
        title: 'Indexación S&P 500 y Dividendos Nobles',
        icon: 'fa-chart-pie',
        budgetPct: 0.35,
        description: 'Desglose del núcleo de renta variable de bajo costo para captura de crecimiento medio de mercado.',
        companies: [
          { ticker: 'VOO', name: 'Vanguard S&P 500 ETF', share: 70, priceEst: 530, div: '1.42%', fcf: 'N/A (ETF)', pe: '26x', stopLoss: 480, takeProfit: 590, badge: 'Ancla Principal', color: 'border-l-blue-500', text: 'Réplica de las 500 compañías norteamericanas de mayor capitalización con costo ultra bajo (0.03%).' },
          { ticker: 'SCHD', name: 'Schwab US Dividend Equity ETF', share: 30, priceEst: 80, div: '3.45%', fcf: 'N/A (ETF)', pe: '16x', stopLoss: 72, takeProfit: 92, badge: 'Crecimiento de Dividendos', color: 'border-l-emerald-500', text: 'Empresas con más de 10 años pagando dividendos en aumento constante. Aporta flujo de caja directo.' }
        ]
      },
      commodities: {
        title: 'Materias Primas, Metales y Energía',
        icon: 'fa-coins',
        budgetPct: 0.20,
        description: 'Activos tangibles para blindar el patrimonio frente a depreciación del dólar e inflación sostenida.',
        companies: [
          { ticker: 'GLD', name: 'SPDR Gold Trust ETF', share: 60, priceEst: 220, div: '0.00%', fcf: 'Oro Físico', pe: 'Reserva', stopLoss: 198, takeProfit: 255, badge: 'Oro Físico', color: 'border-l-amber-400', text: 'Tenencia auditada de lingotes de oro en bóvedas de Londres. Descorrelación frente a bolsas de valores.' },
          { ticker: 'FCX', name: 'Freeport-McMoRan', share: 40, priceEst: 45, div: '1.30%', fcf: '5.2%', pe: '18x', stopLoss: 38, takeProfit: 56, badge: 'Cobre / Transición', color: 'border-l-orange-500', text: 'Mayor productor de cobre del mundo, mineral imprescindible para centros de datos y redes eléctricas.' }
        ]
      },
      cash: {
        title: 'Liquidez Inmediata y Renta Fija',
        icon: 'fa-vault',
        budgetPct: 0.10,
        description: 'Capital en reserva asignado a instrumentos libres de riesgo para capitalizar correcciones de mercado o emergencias.',
        companies: [
          { ticker: 'BIL', name: 'SPDR 1-3 Month T-Bill ETF', share: 60, priceEst: 91, div: '5.15%', fcf: 'Deuda EE.UU.', pe: 'Riesgo Cero', stopLoss: 90, takeProfit: 95, badge: 'Renta Fija Corto Plazo', color: 'border-l-emerald-400', text: 'Bonos del Tesoro de EE.UU. a corto plazo. Interés acumulado de forma segura sin riesgo de crédito.' },
          { ticker: 'USD-CASH', name: 'Efectivo en Broker / Fondo Monetario', share: 40, priceEst: 1, div: '4.80%', fcf: 'Liquidez 100%', pe: 'Inmediato', stopLoss: 1, takeProfit: 1, badge: 'Oportunismo', color: 'border-l-slate-400', text: 'Dinero disponible en la cuenta del broker acumulando interés diario para comprar activos en caídas del >10%.' }
        ]
      }
    };

    const sector = SECTOR_DATA[sectorId] || SECTOR_DATA.tech;
    const sectorBudget = Math.round(amountNum * sector.budgetPct);
    const isTracked = (ticker) => (state.portfolio || []).some(p => p.ticker.toUpperCase() === ticker.toUpperCase());

    return `
      <div id="results-container" class="w-full space-y-8 animate-slide-up">
        
        <!-- BREADCRUMB HEADER NAV -->
        <div class="flex flex-wrap items-center justify-between bg-slate-900 p-4 rounded-2xl border border-slate-800 text-xs gap-3">
          <div class="flex items-center gap-2 text-slate-300 flex-wrap">
            <button id="btn-back-macro" class="text-fintech-emerald font-bold hover:underline flex items-center gap-1 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20 cursor-pointer">
              <i class="fas fa-arrow-left text-xs"></i> Volver a Portafolio General
            </button>
            <span class="text-slate-600">/</span>
            <span class="text-slate-400">Sector Seleccionado:</span>
            <span class="font-bold text-white">${sector.title}</span>
          </div>
          <div class="font-mono text-emerald-400 font-black text-sm">
            Presupuesto Asignado: ${format(sectorBudget)} <span class="text-slate-400 text-xs font-normal">(${Math.round(sector.budgetPct * 100)}% del total)</span>
          </div>
        </div>

        <!-- ENCABEZADO DE SECTOR MICRO -->
        <div class="glass-card p-6 sm:p-8 rounded-3xl border-l-4 border-l-fintech-emerald shadow-2xl">
          <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="px-3 py-1 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <i class="fas ${sector.icon}"></i> Desglose Micro-Nivel
                </span>
                <span class="px-3 py-1 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold text-xs">
                  Presupuesto Activo: ${format(sectorBudget)}
                </span>
              </div>
              <h2 class="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Plan de Compra por Empresa: <span class="text-gradient-emerald">${sector.title}</span>
              </h2>
              <p class="text-sm text-slate-300 mt-2 max-w-3xl leading-relaxed">
                ${sector.description} A continuación verás los montos exactos en dólares, cálculo estimado de acciones, límites de salida técnica (Stop-loss / Take-profit) y las métricas financieras que justifican cada posición.
              </p>
            </div>
          </div>
        </div>

        <!-- TARJETAS DETALLADAS DE EMPRESAS/ETFS -->
        <div class="space-y-4">
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            <i class="fas fa-list-check text-fintech-emerald"></i> Ordenes Individuales de Compra Sugeridas
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-5">
            ${sector.companies.map(c => {
              const companyAmount = Math.round(sectorBudget * (c.share / 100));
              const estimatedShares = Math.max(1, Math.round(companyAmount / c.priceEst));
              const tracked = isTracked(c.ticker);

              return `
                <div class="glass-card p-6 rounded-2xl border-l-4 ${c.color} flex flex-col justify-between hover:bg-slate-900/70 transition-all shadow-lg">
                  <div>
                    <!-- Header de la Empresa -->
                    <div class="flex justify-between items-start mb-3">
                      <div>
                        <span class="px-2.5 py-1 rounded bg-slate-800 text-slate-300 font-extrabold font-mono text-[11px] uppercase tracking-wider">${c.ticker}</span>
                        <span class="text-[10px] text-slate-400 ml-1.5 font-semibold">${c.share}% del sector</span>
                      </div>
                      <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">${c.badge}</span>
                    </div>

                    <h4 class="text-xl font-black text-white mb-1">${c.name}</h4>
                    <p class="text-xs text-slate-300 leading-relaxed mb-4">${c.text}</p>

                    <!-- Métricas Financieras Clave -->
                    <div class="grid grid-cols-3 gap-2 py-2.5 px-3 bg-slate-950/70 rounded-xl border border-slate-800/80 mb-3 text-center">
                      <div>
                        <span class="text-[9px] uppercase text-slate-400 block font-bold">Dividendos</span>
                        <span class="text-xs font-mono font-bold text-emerald-400">${c.div}</span>
                      </div>
                      <div>
                        <span class="text-[9px] uppercase text-slate-400 block font-bold">FCF Yield</span>
                        <span class="text-xs font-mono font-bold text-indigo-300">${c.fcf}</span>
                      </div>
                      <div>
                        <span class="text-[9px] uppercase text-slate-400 block font-bold">Valuación</span>
                        <span class="text-xs font-mono font-bold text-amber-300">${c.pe}</span>
                      </div>
                    </div>

                    <!-- Estrategias de Salida Stop-Loss / Take-Profit (RF-40) -->
                    <div class="grid grid-cols-2 gap-2 py-2 px-3 bg-slate-900/70 rounded-xl border border-slate-800 text-[11px] font-mono mb-4">
                      <div>
                        <span class="text-[9px] uppercase text-rose-400 block font-bold">Stop-Loss (Límite Pérdida)</span>
                        <span class="font-bold text-rose-300">$${c.stopLoss} USD</span>
                      </div>
                      <div>
                        <span class="text-[9px] uppercase text-emerald-400 block font-bold">Take-Profit (Toma Ganancia)</span>
                        <span class="font-bold text-emerald-300">$${c.takeProfit} USD</span>
                      </div>
                    </div>
                  </div>

                  <!-- Bloque Final de Monto, Estimado y Acción -->
                  <div class="pt-4 border-t border-slate-800 space-y-3">
                    <div class="flex justify-between items-end">
                      <div>
                        <span class="text-[10px] uppercase text-slate-400 block font-semibold">Monto Sugerido</span>
                        <div class="text-2xl font-black font-mono text-emerald-400">${format(companyAmount)}</div>
                      </div>
                      <div class="text-right">
                        <span class="text-[10px] uppercase text-slate-400 block font-semibold">Cálculo Estimado</span>
                        <span class="text-xs font-mono font-bold text-slate-200">~${estimatedShares} ${c.ticker === 'USD-CASH' ? 'USD' : 'acciones'}</span>
                      </div>
                    </div>

                    <button class="track-btn w-full py-2.5 px-4 ${tracked ? 'bg-emerald-500 text-slate-950 font-black shadow-glow-emerald border-emerald-400' : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'} font-bold text-xs rounded-xl border flex items-center justify-center gap-2 transition-all cursor-pointer" data-ticker="${c.ticker}" data-name="${c.name}" data-amount="${companyAmount}">
                      <i class="fas ${tracked ? 'fa-check-circle' : 'fa-bookmark'}"></i> 
                      <span>${tracked ? 'Invertido (En Portafolio)' : 'Marcar como Invertido'}</span>
                    </button>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>

        <!-- GRÁFICO DE COMPOSICIÓN MICRO SECTORIAL -->
        <div class="glass-card p-6 rounded-2xl">
          <h3 class="text-lg font-bold text-white mb-1">Distribución de Tickers en este Sector</h3>
          <p class="text-xs text-slate-400 mb-4">Proporción del presupuesto de ${format(sectorBudget)} repartido por activo.</p>
          <div class="relative w-full h-52">
            <canvas id="microSectorChart"></canvas>
          </div>
        </div>

      </div>
    `;
  }

  _renderNicheView(state, intent, amountStr, amountNum) {
    const smhAmount = Math.round(amountNum * 0.70);
    const nvdaAmount = Math.round(amountNum * 0.30);
    const format = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);
    const isTracked = (ticker) => (state.portfolio || []).some(p => p.ticker.toUpperCase() === ticker.toUpperCase());

    return `
      <div id="results-container" class="w-full space-y-8 animate-slide-up">
        <div class="flex items-center justify-between bg-slate-900 p-3.5 rounded-2xl border border-slate-800 text-xs">
          <button id="btn-back-macro" class="text-fintech-emerald font-bold hover:underline flex items-center gap-1 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20 cursor-pointer">
            <i class="fas fa-arrow-left text-xs"></i> Volver a Portafolio General
          </button>
          <span class="font-mono text-cyan-400 font-bold">Monto Objetivo: ${amountStr}</span>
        </div>

        <div class="glass-card p-6 sm:p-8 rounded-3xl border-l-4 border-l-cyan-500 shadow-2xl">
          <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="px-3 py-1 rounded-md bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-bold text-xs uppercase tracking-wider">
                  <i class="fas fa-microchip"></i> Nicho Ultra Especializado
                </span>
                <span class="px-3 py-1 rounded-md bg-rose-500/20 text-rose-400 border border-rose-500/30 font-semibold text-xs">
                  Riesgo / Volatilidad: Alta
                </span>
              </div>
              <h2 class="text-2xl sm:text-4xl font-black text-white tracking-tight">
                Evaluación: <span class="text-cyan-400">Industria Global de Semiconductores</span>
              </h2>
              <p class="text-sm text-slate-300 mt-2 max-w-2xl leading-relaxed">
                Invertir <strong class="text-white font-mono">${amountStr}</strong> en microchips representa comprar la infraestructura crítica del mundo digital.
              </p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <div class="glass-card p-6 rounded-2xl border-l-4 border-l-cyan-400 flex flex-col justify-between">
            <div>
              <span class="px-2.5 py-1 rounded bg-cyan-500/20 text-cyan-300 font-extrabold text-xs uppercase">Estrategia Núcleo (70%)</span>
              <h3 class="text-xl font-bold text-white mt-3">VanEck Semiconductor ETF (SMH)</h3>
              <p class="text-xs text-slate-300 mt-2">Cesta diversificada con las 25 empresas líderes mundiales (NVIDIA, TSMC, ASML, Broadcom).</p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
              <div>
                <span class="text-[10px] uppercase text-slate-400 font-semibold">Monto Sugerido</span>
                <div class="text-2xl font-black font-mono text-cyan-400">${format(smhAmount)}</div>
              </div>
              <button class="track-btn py-2.5 px-4 ${isTracked('SMH') ? 'bg-cyan-500 text-slate-950 font-black' : 'bg-slate-800 hover:bg-slate-700 text-slate-200'} font-bold text-xs rounded-xl border border-slate-700 cursor-pointer" data-ticker="SMH" data-name="VanEck Semiconductor ETF" data-amount="${smhAmount}">
                ${isTracked('SMH') ? 'Invertido' : 'Marcar Invertido'}
              </button>
            </div>
          </div>

          <div class="glass-card p-6 rounded-2xl border-l-4 border-l-emerald-400 flex flex-col justify-between">
            <div>
              <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-extrabold text-xs uppercase">Alpha Directo (30%)</span>
              <h3 class="text-xl font-bold text-white mt-3">NVIDIA Corp (NVDA)</h3>
              <p class="text-xs text-slate-300 mt-2">Líder absoluto en GPUs para centros de datos de IA con márgenes operativos del 60%.</p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
              <div>
                <span class="text-[10px] uppercase text-slate-400 font-semibold">Monto Sugerido</span>
                <div class="text-2xl font-black font-mono text-emerald-400">${format(nvdaAmount)}</div>
              </div>
              <button class="track-btn py-2.5 px-4 ${isTracked('NVDA') ? 'bg-emerald-500 text-slate-950 font-black' : 'bg-slate-800 hover:bg-slate-700 text-slate-200'} font-bold text-xs rounded-xl border border-slate-700 cursor-pointer" data-ticker="NVDA" data-name="NVIDIA Corp" data-amount="${nvdaAmount}">
                ${isTracked('NVDA') ? 'Invertido' : 'Marcar Invertido'}
              </button>
            </div>
          </div>

        </div>
      </div>
    `;
  }

  attachEvents(container, state) {
    // Botón volver a macro
    const backBtn = container.querySelector('#btn-back-macro');
    if (backBtn) backBtn.onclick = () => this.advisor.resetToMacro();

    // Botón ¿Por qué confiar? (Auditoría)
    const trustBtn = container.querySelector('#btn-open-trust-drawer');
    if (trustBtn) trustBtn.onclick = () => this.advisor.openTrustDrawer('allweather');

    // Botones de reintento de error
    const retryBtn = container.querySelector('#btn-retry-prompt');
    if (retryBtn) {
      retryBtn.onclick = () => {
        const input = document.getElementById('prompt-input');
        if (input && input.value) this.advisor.submitPrompt(input.value);
      };
    }

    // Drill down clic en tarjetas de sector
    const sectorCards = container.querySelectorAll('.sector-card-clickable, .sector-btn-drill');
    sectorCards.forEach(card => {
      card.onclick = (e) => {
        e.stopPropagation();
        const sector = card.getAttribute('data-sector');
        if (sector) this.advisor.selectSector(sector);
      };
    });

    // Botones de marcar como invertido / seguir
    const trackBtns = container.querySelectorAll('.track-btn');
    trackBtns.forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        const ticker = btn.getAttribute('data-ticker');
        const name = btn.getAttribute('data-name');
        const amount = Number(btn.getAttribute('data-amount')) || 0;
        this.advisor.toggleTrackAsset({ ticker, name, amount });
      };
    });

    // Renderizar gráficos si corresponde
    if (!state.activeSector && document.getElementById('projectionChart')) {
      const amount = state.predictionIntent?.requestedAmount || 20000;
      chartManager.renderProjectionChart('projectionChart', amount);
    } else if (state.activeSector && document.getElementById('microSectorChart')) {
      const sectorId = state.activeSector;
      const budget = Math.round((state.predictionIntent?.requestedAmount || 20000) * 0.35);
      if (sectorId === 'tech') {
        chartManager.renderBarChart('microSectorChart', ['AAPL', 'META', 'MSFT', 'NVDA'], [Math.round(budget*0.3), Math.round(budget*0.25), Math.round(budget*0.25), Math.round(budget*0.2)]);
      } else if (sectorId === 'sp500') {
        chartManager.renderBarChart('microSectorChart', ['VOO', 'SCHD'], [Math.round(budget*0.7), Math.round(budget*0.3)]);
      } else if (sectorId === 'commodities') {
        chartManager.renderBarChart('microSectorChart', ['GLD', 'FCX'], [Math.round(budget*0.6), Math.round(budget*0.4)]);
      } else {
        chartManager.renderBarChart('microSectorChart', ['BIL', 'USD-CASH'], [Math.round(budget*0.6), Math.round(budget*0.4)]);
      }
    }
  }
}
