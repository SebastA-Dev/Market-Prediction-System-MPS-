/**
 * Componente: UserModalComponent
 * Modal integral de usuario con portafolio guardado, perfil y autenticación Micronaut (UC-09a, UC-10).
 */
export class UserModalComponent {
  /**
   * @param {Object} controllers
   * @param {import('../../infrastructure/adapters/in/controllers/PortfolioController.js').PortfolioController} controllers.portfolio
   * @param {import('../../infrastructure/adapters/in/controllers/AuthController.js').AuthController} controllers.auth
   */
  constructor({ portfolio, auth }) {
    this.portfolio = portfolio;
    this.auth = auth;
  }

  render(state) {
    const isOpen = state.isUserModalOpen;
    const activeTab = state.userModalTab || 'tracked';
    const user = state.user || {
      id: null,
      displayName: 'Invitado',
      email: '',
      riskProfile: '',
      initials: 'IN',
      isAuthenticated: false
    };

    const portfolio = state.portfolio || [];
    let totalTracked = 0;
    portfolio.forEach(item => totalTracked += (Number(item.amount) || 0));
    const totalTrackedFormatted = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(totalTracked);

    return `
      <!-- MODAL DE USUARIO Y CONFIGURACIÓN -->
      <div id="user-modal-overlay" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-[80] ${isOpen ? '' : 'hidden opacity-0'} transition-opacity duration-300 flex items-center justify-center p-4">
        <div class="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
          
          <!-- User Modal Header -->
          <div class="p-6 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white font-extrabold flex items-center justify-center text-lg shadow-lg">
                ${user.initials || 'AW'}
              </div>
              <div>
                <h2 class="text-lg font-bold text-white flex items-center gap-2">
                  <span id="modal-user-display-name">${user.displayName}</span>
                  <span class="text-[10px] px-2 py-0.5 rounded-full ${user.isAuthenticated ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400 border border-slate-700'} font-bold">
                    ${user.isAuthenticated ? 'Verificado (JWT)' : 'Invitado'}
                  </span>
                </h2>
                <p class="text-xs text-slate-400 font-mono" id="modal-user-display-email">${user.email}</p>
              </div>
            </div>
            <button id="btn-close-user-modal" class="w-8 h-8 rounded-xl bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center cursor-pointer">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <!-- User Modal Navigation Tabs -->
          <div class="flex border-b border-slate-800 bg-slate-900/50 text-xs font-bold">
            <button id="tab-btn-tracked" class="flex-1 py-3 px-4 border-b-2 ${activeTab === 'tracked' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-white'} transition-all flex items-center justify-center gap-2 cursor-pointer">
              <i class="fas fa-vault"></i> Mis Inversiones Guardadas (<span id="user-tracked-count">${portfolio.length}</span>)
            </button>
            <button id="tab-btn-settings" class="flex-1 py-3 px-4 border-b-2 ${activeTab === 'settings' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-white'} transition-all flex items-center justify-center gap-2 cursor-pointer">
              <i class="fas fa-id-card"></i> Mi Perfil
            </button>
            <button id="tab-btn-auth" class="flex-1 py-3 px-4 border-b-2 ${activeTab === 'auth' ? 'border-purple-500 text-purple-400' : 'border-transparent text-slate-400 hover:text-white'} transition-all flex items-center justify-center gap-2 cursor-pointer">
              <i class="fas fa-key"></i> Sesión Micronaut
            </button>
          </div>

          <!-- Modal Tab 1: Investments Tracked -->
          <div id="user-tab-tracked" class="p-6 overflow-y-auto custom-scrollbar space-y-4 ${activeTab === 'tracked' ? '' : 'hidden'}">
            <div class="flex items-center justify-between text-xs text-slate-400 bg-slate-900 p-3 rounded-xl border border-slate-800">
              <span>Capital Seguimiento Activo:</span>
              <span class="font-mono font-bold text-emerald-400 text-sm" id="user-total-tracked-amount">${totalTrackedFormatted} USD</span>
            </div>

            <div class="space-y-3" id="user-tracked-list">
              ${
                portfolio.length === 0
                  ? `
                    <div class="text-center py-8 text-xs text-slate-400">
                      <i class="fas fa-folder-open text-2xl mb-2 text-slate-600 block"></i>
                      Aún no has marcado ninguna inversión como invertida.
                    </div>
                  `
                  : portfolio.map(item => `
                    <div class="p-3.5 bg-slate-900 rounded-xl border border-slate-800 flex items-center justify-between">
                      <div>
                        <div class="flex items-center gap-2 mb-1">
                          <span class="font-mono font-bold text-xs bg-slate-800 text-emerald-400 px-2 py-0.5 rounded border border-slate-700">${item.ticker}</span>
                          <span class="font-bold text-white text-xs">${item.name}</span>
                        </div>
                        <span class="text-[10px] text-slate-400">Registrado: ${item.followingSince} • Estado: <strong class="text-emerald-400">${item.status}</strong></span>
                      </div>
                      <div class="text-right flex items-center gap-3">
                        <div>
                          <div class="font-mono font-bold text-white text-sm">${item.formattedAmount}</div>
                          <span class="text-[10px] text-emerald-400 font-bold">${item.change}</span>
                        </div>
                        <button class="btn-delete-tracked w-7 h-7 rounded-lg bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-500 flex items-center justify-center text-xs transition-all cursor-pointer" data-ticker="${item.ticker}" title="Eliminar de portafolio">
                          <i class="fas fa-trash"></i>
                        </button>
                      </div>
                    </div>
                  `).join('')
              }
            </div>
          </div>

          <!-- Modal Tab 2: Datos reales de la cuenta recibidos de Micronaut -->
          <div id="user-tab-settings" class="p-6 overflow-y-auto custom-scrollbar space-y-5 ${activeTab === 'settings' ? '' : 'hidden'}">
            ${user.isAuthenticated ? `
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Correo de la cuenta</label>
                  <div class="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white">${user.email}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Identificador de usuario</label>
                  <div class="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white font-mono break-all">${user.id || 'No disponible'}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Cuenta creada</label>
                  <div class="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white">${user.createdAt ? new Date(user.createdAt).toLocaleString() : 'Verificada por el servicio de autenticación'}</div>
                </div>
                <p class="text-[11px] text-slate-500">Estos datos provienen de la cuenta autenticada en el backend.</p>
              </div>
            ` : `
              <div class="text-center py-8 text-xs text-slate-400">Inicia sesión para consultar los datos de tu perfil.</div>
            `}
          </div>

          <!-- Modal Tab 3: Micronaut Auth -->
          <div id="user-tab-auth" class="p-6 overflow-y-auto custom-scrollbar space-y-5 ${activeTab === 'auth' ? '' : 'hidden'}">
            <div class="p-3.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs text-purple-300 leading-relaxed">
              <i class="fas fa-shield-cat mr-1"></i> <strong>Integración con Backend Micronaut (Puerto 8080):</strong> Inicia sesión o regístrate para validar tu cuenta en PostgreSQL y consultar los datos asociados mediante JWT.
            </div>

            ${user.isAuthenticated ? `
              <div class="p-4 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 space-y-2 text-xs">
                <div class="text-emerald-300 font-bold">Sesión autenticada</div>
                <div class="text-slate-300">${user.email}</div>
                <div class="text-slate-500 font-mono break-all">${user.id || ''}</div>
                <button id="btn-logout-session" class="mt-2 px-4 py-1.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold hover:bg-rose-500/30 transition-all cursor-pointer">Cerrar Sesión</button>
              </div>
            ` : `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Login Form -->
              <div class="glass-card p-4 rounded-2xl border border-slate-800 space-y-3">
                <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <i class="fas fa-right-to-bracket text-emerald-400"></i> Iniciar Sesión (POST /api/v1/auth/login)
                </h4>
                <div>
                  <label class="block text-[10px] text-slate-400 mb-1">Email</label>
                  <input type="email" id="input-login-email" placeholder="usuario@quant.io" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white">
                </div>
                <div>
                  <label class="block text-[10px] text-slate-400 mb-1">Contraseña</label>
                  <input type="password" id="input-login-password" placeholder="••••••••" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white">
                </div>
                <button id="btn-exec-login" class="w-full py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-xl transition-all cursor-pointer">
                  Entrar
                </button>
              </div>

              <!-- Register Form -->
              <div class="glass-card p-4 rounded-2xl border border-slate-800 space-y-3">
                <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <i class="fas fa-user-plus text-indigo-400"></i> Registro (POST /api/v1/users)
                </h4>
                <div>
                  <label class="block text-[10px] text-slate-400 mb-1">Email</label>
                  <input type="email" id="input-register-email" placeholder="nuevo@quant.io" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white">
                </div>
                <div>
                  <label class="block text-[10px] text-slate-400 mb-1">Contraseña</label>
                  <input type="password" id="input-register-password" placeholder="••••••••" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white">
                </div>
                <button id="btn-exec-register" class="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl transition-all cursor-pointer">
                  Crear Cuenta
                </button>
              </div>
            </div>
            `}
          </div>

        </div>
      </div>
    `;
  }

  attachEvents(container) {
    const closeBtn = container.querySelector('#btn-close-user-modal');
    if (closeBtn) closeBtn.onclick = () => this.portfolio.closeModal();

    const overlay = container.querySelector('#user-modal-overlay');
    if (overlay) {
      overlay.onclick = (e) => {
        if (e.target === overlay) this.portfolio.closeModal();
      };
    }

    // Tabs
    const tabTracked = container.querySelector('#tab-btn-tracked');
    const tabSettings = container.querySelector('#tab-btn-settings');
    const tabAuth = container.querySelector('#tab-btn-auth');

    if (tabTracked) tabTracked.onclick = () => this.portfolio.switchTab('tracked');
    if (tabSettings) tabSettings.onclick = () => this.portfolio.switchTab('settings');
    if (tabAuth) tabAuth.onclick = () => this.portfolio.switchTab('auth');

    // Botones eliminar inversión
    const deleteBtns = container.querySelectorAll('.btn-delete-tracked');
    deleteBtns.forEach(btn => {
      btn.onclick = () => {
        const ticker = btn.getAttribute('data-ticker');
        if (ticker) this.portfolio.deleteItem(ticker);
      };
    });

    // Login
    const loginBtn = container.querySelector('#btn-exec-login');
    if (loginBtn) {
      loginBtn.onclick = () => {
        const email = container.querySelector('#input-login-email')?.value;
        const password = container.querySelector('#input-login-password')?.value;
        this.auth.login(email, password);
      };
    }

    // Register
    const registerBtn = container.querySelector('#btn-exec-register');
    if (registerBtn) {
      registerBtn.onclick = () => {
        const email = container.querySelector('#input-register-email')?.value;
        const password = container.querySelector('#input-register-password')?.value;
        this.auth.register(email, password);
      };
    }

    // Logout
    const logoutBtn = container.querySelector('#btn-logout-session');
    if (logoutBtn) logoutBtn.onclick = () => this.auth.logout();
  }
}
