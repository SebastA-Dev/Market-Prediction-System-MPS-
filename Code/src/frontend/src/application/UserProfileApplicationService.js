import { IUserProfileUseCase } from '../domain/ports/in/IAuthUseCases.js';
import { User } from '../domain/models/User.js';

/** Consulta la identidad desde el backend; el perfil nunca se inventa en el navegador. */
export class UserProfileApplicationService extends IUserProfileUseCase {
  constructor(authRepository, storagePort) {
    super();
    this.authRepository = authRepository;
    this.storagePort = storagePort;
  }

  async getProfile() {
    const token = this.storagePort.getItem('mps_auth_token');
    if (!token) return new User({ id: null, displayName: 'Invitado' });

    const identity = await this.authRepository.getMe(token);
    let cached = {};
    try {
      cached = JSON.parse(this.storagePort.getItem('mps_user_profile') || '{}');
    } catch (error) {
      this.storagePort.removeItem('mps_user_profile');
    }

    const email = identity.email || '';
    const user = new User({
      id: identity.id || null,
      email,
      displayName: email.split('@')[0] || 'Usuario',
      riskProfile: '',
      createdAt: cached.createdAt || null,
      token
    });
    this.storagePort.setItem('mps_user_profile', JSON.stringify({
      id: user.id,
      email: user.email,
      displayName: user.displayName,
      riskProfile: user.riskProfile,
      createdAt: user.createdAt
    }));
    return user;
  }

  async updateProfile() {
    throw new Error('El backend todavía no ofrece un endpoint para modificar el perfil.');
  }
}
