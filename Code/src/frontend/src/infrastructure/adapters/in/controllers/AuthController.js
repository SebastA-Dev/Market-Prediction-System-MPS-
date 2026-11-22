import { globalAppState } from '../state/AppState.js';

/**
 * Controlador de Entrada (Primary Adapter): AuthController
 * Gestiona la autenticación del usuario contra el microservicio Micronaut.
 */
export class AuthController {
  /**
   * @param {import('../../../../application/AuthApplicationService.js').AuthApplicationService} authService
   * @param {import('../../../../application/UserProfileApplicationService.js').UserProfileApplicationService} profileService
   * @param {import('../../../../application/PortfolioApplicationService.js').PortfolioApplicationService} portfolioService
   */
  constructor(authService, profileService, portfolioService) {
    this.authService = authService;
    this.profileService = profileService;
    this.portfolioService = portfolioService;
  }

  async initSession() {
    try {
      const user = await this.authService.checkSession();
      globalAppState.set({ user });
      const portfolio = await this.portfolioService.getPortfolio();
      globalAppState.set({ portfolio });
    } catch (err) {
      console.warn('Sesión no inicializada:', err);
    }
  }

  async login(email, password) {
    if (!email || !password) {
      globalAppState.showToast('Por favor completa correo y contraseña.', 'info');
      return;
    }

    try {
      const user = await this.authService.login(email, password);
      globalAppState.set({ user });
      globalAppState.showToast(`¡Bienvenido de nuevo, ${user.displayName}!`, 'success');
      
      // Cargar portafolio real del usuario autenticado
      const portfolio = await this.portfolioService.getPortfolio();
      globalAppState.set({ portfolio, userModalTab: 'tracked' });
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

  async saveProfile(name, email, riskProfile) {
    try {
      const updated = await this.profileService.updateProfile({
        displayName: name,
        email,
        riskProfile
      });
      globalAppState.set({ user: updated, isUserModalOpen: false });
      globalAppState.showToast('Perfil actualizado correctamente.', 'success');
    } catch (err) {
      globalAppState.showToast(`Error al guardar perfil: ${err.message}`, 'info');
    }
  }

  logout() {
    this.authService.logout();
    this.initSession();
    globalAppState.showToast('Sesión cerrada.', 'info');
  }
}
