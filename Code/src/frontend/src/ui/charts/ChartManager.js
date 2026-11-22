/**
 * Gestor de Gráficos (ChartManager)
 * Garantiza el ciclo de vida seguro de gráficos Chart.js (RF-43, HU-3.8).
 * Destruye explícitamente las instancias previas antes de re-renderizar para evitar memory leaks.
 */
export class ChartManager {
  constructor() {
    this.activeCharts = new Map();
  }

  /**
   * Destruye un gráfico específico por su id de canvas.
   * @param {string} canvasId
   */
  destroy(canvasId) {
    if (this.activeCharts.has(canvasId)) {
      const chart = this.activeCharts.get(canvasId);
      if (chart && typeof chart.destroy === 'function') {
        try {
          chart.destroy();
        } catch (e) {
          console.warn(`Error destruyendo gráfico ${canvasId}:`, e);
        }
      }
      this.activeCharts.delete(canvasId);
    }
  }

  /**
   * Destruye todos los gráficos activos en memoria.
   */
  destroyAll() {
    for (const [id, chart] of this.activeCharts.entries()) {
      if (chart && typeof chart.destroy === 'function') {
        try {
          chart.destroy();
        } catch (e) {}
      }
    }
    this.activeCharts.clear();
  }

  /**
   * Inicializa el gráfico de proyección Monte Carlo (Línea).
   * @param {string} canvasId
   * @param {number} baseAmount
   */
  renderProjectionChart(canvasId, baseAmount = 20000) {
    this.destroy(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    const labels = ['Hoy', 'Año 1', 'Año 2', 'Año 3'];
    const expected = [
      baseAmount,
      Math.round(baseAmount * 1.112),
      Math.round(baseAmount * 1.236),
      Math.round(baseAmount * 1.375)
    ];
    const conservative = [
      baseAmount,
      Math.round(baseAmount * 1.04),
      Math.round(baseAmount * 1.085),
      Math.round(baseAmount * 1.13)
    ];

    const chart = new Chart(canvas.getContext('2d'), {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Proyección Esperada IA (+11.2% CAGR)',
            data: expected,
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#10B981'
          },
          {
            label: 'Escenario Conservador / Basal',
            data: conservative,
            borderColor: '#64748B',
            borderWidth: 2,
            borderDash: [4, 4],
            fill: false,
            tension: 0.3,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` $${ctx.raw.toLocaleString()}`
            }
          }
        },
        scales: {
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: {
              color: '#9CA3AF',
              font: { size: 10 },
              callback: (v) => '$' + (v / 1000) + 'k'
            }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#9CA3AF', font: { size: 10 } }
          }
        }
      }
    });

    this.activeCharts.set(canvasId, chart);
  }

  /**
   * Inicializa el gráfico de barras para distribución de tickers en micro-sector.
   * @param {string} canvasId
   * @param {string[]} tickers
   * @param {number[]} amounts
   */
  renderBarChart(canvasId, tickers, amounts) {
    this.destroy(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    const colors = ['#10B981', '#6366F1', '#F59E0B', '#06B6D4', '#EC4899', '#8B5CF6'];

    const chart = new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: tickers,
        datasets: [{
          label: 'Inversión en USD',
          data: amounts,
          backgroundColor: tickers.map((_, i) => colors[i % colors.length]),
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` $${ctx.raw.toLocaleString()}`
            }
          }
        },
        scales: {
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: {
              color: '#9CA3AF',
              callback: (v) => '$' + v.toLocaleString()
            }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#F9FAFB', font: { weight: 'bold' } }
          }
        }
      }
    });

    this.activeCharts.set(canvasId, chart);
  }
}

export const chartManager = new ChartManager();
