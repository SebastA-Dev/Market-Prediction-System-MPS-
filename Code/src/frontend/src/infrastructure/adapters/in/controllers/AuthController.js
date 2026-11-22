import { globalAppState } from '../state/AppState.js';

/**
 * Controlador de Entrada (Primary Adapter): AuthController
 * Gestiona la autenticación del usuario contra el microservicio Micronaut.
 */
export class AuthController {
  /**
   * @param {import('../../../../application/AuthApplicationService.js').AuthApplicationService} authService
   * @param {import('../../../../application/PortfolioApplicationService.js').PortfolioApplicationService} portfolioService
   */
  constructor(authService, portfolioService) {
    this.authService = authService;
    this.portfolioService = portfolioService;
  }

  async initSession() {
    const user = await this.authService.checkSession();
    globalAppState.set({ user });
    if (!user.isAuthenticated) {
      globalAppState.set({ portfolio: [] });
      return;
    }

    try {
      const portfolio = await this.portfolioService.getPortfolio();
      globalAppState.set({ portfolio });
    } catch (err) {
      console.warn('No se pudo cargar el portafolio:', err);
      globalAppState.set({ portfolio: [] });
    }
  }

  async login(email, password) {
    if (!email || !password) {
      globalAppState.showToast('Por favor completa correo y contraseña.', 'info');
      return;
    }

    try {
      const user = await this.authService.login(email, password);
      globalAppState.set({ user, isUserModalOpen: true, userModalTab: 'settings', portfolio: [] });
      globalAppState.showToast(`¡Bienvenido de nuevo, ${user.displayName}!`, 'success');

      try {
        const portfolio = await this.portfolioService.getPortfolio();
        globalAppState.set({ portfolio });
      } catch (portfolioError) {
        console.warn('No se pudo cargar el portafolio:', portfolioError);
        globalAppState.showToast('Sesión iniciada; no se pudieron cargar las inversiones.', 'info');
      }
    } catch (err) {
      const msg = err.status === 401 ? 'Credenciales incorrectas' : (err.message || 'Error de inicio de sesión');
      globalAppState.showToast(msg, 'info');
    }
  }

  async register(email, password) {
    if (!email || !password) {
      globalAppState.showToast('Por favor completa correo y contraseña.', 'info');
      return;
    }

    try {
      await this.authService.register(email, password);
      globalAppState.showToast('Usuario registrado exitosamente. Iniciando sesión...', 'success');
      await this.login(email, password);
    } catch (err) {
      const msg = err.status === 409 ? 'El correo ya se encuentra registrado' : (err.message || 'Error al registrar usuario');
      globalAppState.showToast(msg, 'info');
    }
  }

  logout() {
    this.authService.logout();
    globalAppState.set({
      user: this.authService.guestUser(),
      portfolio: [],
      isUserModalOpen: false,
      userModalTab: 'auth'
    });
    globalAppState.showToast('Sesión cerrada.', 'info');
  }
}
