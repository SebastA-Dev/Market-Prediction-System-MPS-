/**
 * Componente: HeaderComponent
 * Barra superior fija con marca, navegación entre vistas, notificaciones y perfil de usuario.
 */
export class HeaderComponent {
  /**
   * @param {Object} controllers
   * @param {import('../../infrastructure/adapters/in/controllers/AdvisorController.js').AdvisorController} controllers.advisor
   * @param {import('../../infrastructure/adapters/in/controllers/NotificationController.js').NotificationController} controllers.notification
   * @param {import('../../infrastructure/adapters/in/controllers/PortfolioController.js').PortfolioController} controllers.portfolio
   */
  constructor({ advisor, notification, portfolio }) {
    this.advisor = advisor;
    this.notification = notification;
    this.portfolio = portfolio;
  }

  render(state) {
    const isAdvisor = state.currentView === 'advisor';
    const unreadCount = (state.notifications || []).filter(n => !n.read).length;
    const user = state.user || { displayName: 'Alex Wright', initials: 'AW' };

    return `
      <header class="fixed w-full top-0 z-40 glass-card border-b border-fintech-cardBorder/60 h-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
          
          <!-- Logo & Brand -->
          <div class="flex items-center gap-3 cursor-pointer group" id="brand-logo-btn">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-fintech-emeraldDark via-fintech-emerald to-emerald-400 flex items-center justify-center shadow-glow-emerald transition-transform group-hover:scale-105">
              <i class="fas fa-chart-line text-slate-950 text-lg font-extrabold"></i>
            </div>
            <div class="flex flex-col">
              <span class="font-extrabold text-xl tracking-tight leading-none text-white">NexGen<span class="text-fintech-emerald">Quant</span></span>
              <span class="text-[10px] text-fintech-textMuted tracking-wider uppercase font-semibold mt-0.5">Consejería de Inversión IA</span>
            </div>
          </div>
          
          <!-- Nav Controls: Advisor, Investment Guide, Notifications, User Profile -->
          <div class="flex items-center gap-2 sm:gap-3">
            
            <!-- Toggle View: Advisor Mode -->
            <button id="nav-advisor-btn" class="flex items-center gap-2 px-3 py-2 rounded-xl ${
              isAdvisor
                ? 'bg-fintech-emerald/20 text-emerald-400 border border-fintech-emerald/40 font-bold'
                : 'bg-slate-900/90 hover:bg-slate-800 text-slate-300 border border-slate-700/80 font-semibold'
            } transition-all text-xs shadow-sm">
              <i class="fas fa-robot text-sm"></i>
              <span class="hidden sm:inline">Consejero IA</span>
            </button>

            <!-- Dedicated Page: Guía de Inversión -->
            <button id="nav-guide-btn" class="flex items-center gap-2 px-3 py-2 rounded-xl ${
              !isAdvisor
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-bold'
                : 'bg-slate-900/90 hover:bg-slate-800 text-slate-300 border border-slate-700/80 font-semibold'
            } transition-all text-xs shadow-sm">
              <i class="fas fa-graduation-cap text-indigo-400 text-sm"></i>
              <span class="hidden sm:inline">Guía de Inversión</span>
            </button>

            <div class="h-6 w-px bg-slate-800 mx-1"></div>

            <!-- Notifications Center Bell -->
            <div class="relative">
              <button id="notif-bell-btn" class="w-10 h-10 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-white flex items-center justify-center relative transition-all">
                <i class="fas fa-bell text-sm"></i>
                <span id="notif-badge" class="${unreadCount > 0 ? '' : 'hidden'} absolute -top-1 -right-1 w-5 h-5 bg-emerald-500 text-slate-950 text-[10px] font-black rounded-full flex items-center justify-center border-2 border-slate-950">
                  ${unreadCount}
                </span>
              </button>

              <!-- Notifications Dropdown Box -->
              <div id="notif-dropdown" class="${state.isNotifMenuOpen ? '' : 'hidden'} absolute right-0 mt-3 w-80 sm:w-96 glass-card rounded-2xl border border-slate-800 shadow-2xl z-50 p-4 animate-fade-in">
                <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
                  <div class="flex items-center gap-2">
                    <i class="fas fa-chart-line text-emerald-400 text-xs"></i>
                    <h4 class="font-bold text-white text-xs uppercase tracking-wider">Cambios en Métricas Guardadas</h4>
                  </div>
                  <button id="clear-notifs-btn" class="text-[10px] text-slate-400 hover:text-emerald-400 font-semibold">Marcar leídas</button>
                </div>
                <div class="space-y-2.5 max-h-72 overflow-y-auto custom-scrollbar">
                  ${
                    (state.notifications || []).length === 0
                      ? `<div class="p-4 text-center text-xs text-slate-400">Sin notificaciones nuevas.</div>`
                      : state.notifications.map(n => `
                        <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs hover:border-slate-700 transition-all flex items-start gap-2.5">
                          <span class="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 font-bold font-mono text-[10px] flex items-center justify-center shrink-0 border border-emerald-500/30">${n.ticker}</span>
                          <div class="flex-1">
                            <div class="flex justify-between items-center mb-0.5">
                              <span class="font-bold text-white text-xs">${n.title}</span>
                              <span class="text-[9px] text-slate-500">${n.time}</span>
                            </div>
                            <p class="text-[11px] text-slate-300 leading-tight">${n.desc}</p>
                          </div>
                        </div>
                      `).join('')
                  }
                </div>
              </div>
            </div>

            <!-- User Profile Menu -->
            <button id="user-profile-header-btn" class="flex items-center gap-2.5 pl-1.5 pr-3 py-1 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 transition-all text-xs text-white">
              <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 text-white font-bold flex items-center justify-center text-xs shadow-md">
                ${user.initials || 'AW'}
              </div>
              <span class="hidden md:inline font-semibold text-slate-200" id="header-user-name">${user.displayName || 'Alex Wright'}</span>
              <i class="fas fa-chevron-down text-[10px] text-slate-400 ml-0.5"></i>
            </button>

          </div>
        </div>
      </header>
    `;
  }

  attachEvents(container) {
    const brandBtn = container.querySelector('#brand-logo-btn');
    if (brandBtn) brandBtn.onclick = () => this.advisor.switchView('advisor');

    const navAdvBtn = container.querySelector('#nav-advisor-btn');
    if (navAdvBtn) navAdvBtn.onclick = () => this.advisor.switchView('advisor');

    const navGuideBtn = container.querySelector('#nav-guide-btn');
    if (navGuideBtn) navGuideBtn.onclick = () => this.advisor.switchView('guide');

    const notifBtn = container.querySelector('#notif-bell-btn');
    if (notifBtn) notifBtn.onclick = () => this.notification.toggleMenu();

    const clearNotifBtn = container.querySelector('#clear-notifs-btn');
    if (clearNotifBtn) clearNotifBtn.onclick = () => this.notification.clearAll();

    const userProfileBtn = container.querySelector('#user-profile-header-btn');
    if (userProfileBtn) userProfileBtn.onclick = () => this.portfolio.openModal('tracked');
  }
}
