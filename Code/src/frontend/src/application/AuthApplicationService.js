import { IAuthUseCase } from '../domain/ports/in/IAuthUseCases.js';
import { User } from '../domain/models/User.js';

/**
 * Servicio de Aplicación: AuthApplicationService
 * Gestiona el ciclo de vida de la autenticación de usuarios contra Micronaut.
 */
export class AuthApplicationService extends IAuthUseCase {
  /**
   * @param {import('../domain/ports/out/IAuthRepositoryPort.js').IAuthRepositoryPort} authRepository
   * @param {import('../domain/ports/out/INotificationAndStoragePorts.js').IStoragePort} storagePort
   */
  constructor(authRepository, storagePort) {
    super();
    this.authRepository = authRepository;
    this.storagePort = storagePort;
  }

  /**
   * Inicia sesión llamando al endpoint POST /api/v1/auth/login.
   * @param {string} email
   * @param {string} password
   * @returns {Promise<User>}
   */
  async login(email, password) {
    const result = await this.authRepository.login(email, password);
    const token = result.access_token || result.token;
    
    this.storagePort.setItem('mps_auth_token', token);
    
    const user = new User({
      id: result.user?.id || 'user-default',
      email: result.user?.email || email,
      displayName: result.user?.email?.split('@')[0] || 'Alex Wright',
      token: token
    });
    
    this.storagePort.setItem('mps_user_profile', JSON.stringify({
      id: user.id,
      email: user.email,
      displayName: user.displayName,
      riskProfile: user.riskProfile
    }));
    
    return user;
  }

  /**
   * Registra un nuevo usuario llamando al endpoint POST /api/v1/users.
   * @param {string} email
   * @param {string} password
   * @returns {Promise<User>}
   */
  async register(email, password) {
    const registered = await this.authRepository.register(email, password);
    return new User({
      id: registered.id,
      email: registered.email,
      createdAt: registered.created_at || registered.createdAt
    });
  }

  /**
   * Valida la sesión activa contra el endpoint GET /api/v1/auth/me si hay token guardado.
   * @returns {Promise<User|null>}
   */
  async checkSession() {
    const token = this.storagePort.getItem('mps_auth_token');
    const cachedProfile = this.storagePort.getItem('mps_user_profile');
    
    let defaultUser = new User({
      id: 'usr-alex-wright',
      email: 'alex.wright@quant.io',
      displayName: 'Alex Wright',
      riskProfile: 'Moderado'
    });

    if (cachedProfile) {
      try {
        const parsed = JSON.parse(cachedProfile);
        defaultUser = new User({ ...parsed, token: token || null });
      } catch (e) {
        // Fallback a default
      }
    }

    if (!token) {
      return defaultUser;
    }

    try {
      const me = await this.authRepository.getMe(token);
      defaultUser.id = me.name || me.id || defaultUser.id;
      defaultUser.email = me.email || defaultUser.email;
      defaultUser.token = token;
      return defaultUser;
    } catch (err) {
      console.warn('Token expirado o inválido, restableciendo sesión local:', err.message);
      this.storagePort.removeItem('mps_auth_token');
      return defaultUser;
    }
  }

  logout() {
    this.storagePort.removeItem('mps_auth_token');
  }
}
