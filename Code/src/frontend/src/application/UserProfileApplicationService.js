import { IUserProfileUseCase } from '../domain/ports/in/IAuthUseCases.js';
import { User } from '../domain/models/User.js';

/**
 * Servicio de Aplicación: UserProfileApplicationService
 * Permite consultar y modificar ajustes de perfil de usuario.
 */
export class UserProfileApplicationService extends IUserProfileUseCase {
  /**
   * @param {import('../domain/ports/out/IAuthRepositoryPort.js').IAuthRepositoryPort} authRepository
   * @param {import('../domain/ports/out/INotificationAndStoragePorts.js').IStoragePort} storagePort
   */
  constructor(authRepository, storagePort) {
    super();
    this.authRepository = authRepository;
    this.storagePort = storagePort;
  }

  async getProfile() {
    const cached = this.storagePort.getItem('mps_user_profile');
    if (cached) {
      try {
        return new User(JSON.parse(cached));
      } catch (e) {}
    }
    return new User({
      id: 'usr-alex-wright',
      email: 'alex.wright@quant.io',
      displayName: 'Alex Wright',
      riskProfile: 'Moderado'
    });
  }

  async updateProfile(profileData) {
    const token = this.storagePort.getItem('mps_auth_token');
    if (token) {
      try {
        await this.authRepository.updateProfile(token, profileData);
      } catch (err) {
        console.info('Endpoint remoto de actualización de perfil no disponible aún:', err.message);
      }
    }

    const current = await this.getProfile();
    const updated = new User({
      ...current,
      ...profileData
    });

    this.storagePort.setItem('mps_user_profile', JSON.stringify({
      id: updated.id,
      email: updated.email,
      displayName: updated.displayName,
      riskProfile: updated.riskProfile
    }));

    return updated;
  }
}
