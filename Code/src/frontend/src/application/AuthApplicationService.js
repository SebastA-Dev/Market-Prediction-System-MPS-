import { IAuthUseCase } from '../domain/ports/in/IAuthUseCases.js';
import { User } from '../domain/models/User.js';

/** Gestiona el registro, la sesión y la identidad persistida por Micronaut. */
export class AuthApplicationService extends IAuthUseCase {
  constructor(authRepository, storagePort) {
    super();
    this.authRepository = authRepository;
    this.storagePort = storagePort;
  }

  async login(email, password) {
    const result = await this.authRepository.login(email, password);
    // Micronaut serializa LoginResponse como accessToken (camelCase).
    const token = result.accessToken || result.access_token || result.token;
    if (!token) throw new Error('El servidor no devolvió el token de autenticación.');

    this.storagePort.setItem('mps_auth_token', token);
    try {
      const identity = await this.authRepository.getMe(token);
      const user = this._mapUser({ ...result.user, ...identity }, token);
      this._storeProfile(user);
      return user;
    } catch (error) {
      this.storagePort.removeItem('mps_auth_token');
      throw error;
    }
  }

  async register(email, password) {
    const registered = await this.authRepository.register(email, password);
    return new User({
      id: registered.id,
      email: registered.email,
      displayName: registered.email?.split('@')[0] || 'Usuario',
      createdAt: registered.createdAt || registered.created_at
    });
  }

  async checkSession() {
    const token = this.storagePort.getItem('mps_auth_token');
    if (!token) return this.guestUser();

    let cached = {};
    try {
      cached = JSON.parse(this.storagePort.getItem('mps_user_profile') || '{}');
    } catch (error) {
      this.storagePort.removeItem('mps_user_profile');
    }

    try {
      const identity = await this.authRepository.getMe(token);
      const user = this._mapUser(identity, token, cached);
      this._storeProfile(user);
      return user;
    } catch (error) {
      this.storagePort.removeItem('mps_auth_token');
      this.storagePort.removeItem('mps_user_profile');
      console.warn('Token expirado o inválido; sesión cerrada:', error.message);
      return this.guestUser();
    }
  }

  _mapUser(data = {}, token = null, cached = {}) {
    const email = data.email || cached.email || '';
    return new User({
      id: data.id || cached.id || null,
      email,
      displayName: email.split('@')[0] || 'Usuario',
      riskProfile: '',
      createdAt: data.createdAt || data.created_at || cached.createdAt || null,
      token
    });
  }

  _storeProfile(user) {
    this.storagePort.setItem('mps_user_profile', JSON.stringify({
      id: user.id,
      email: user.email,
      displayName: user.displayName,
      riskProfile: user.riskProfile,
      createdAt: user.createdAt
    }));
  }

  guestUser() {
    return new User({ id: null, email: '', displayName: 'Invitado', riskProfile: '' });
  }

  logout() {
    this.storagePort.removeItem('mps_auth_token');
    this.storagePort.removeItem('mps_user_profile');
  }
}
