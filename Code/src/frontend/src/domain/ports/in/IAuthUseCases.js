/**
 * Puertos de Entrada para Autenticación y Usuarios (Inbound Ports)
 */

export class IAuthUseCase {
  /**
   * @param {string} email
   * @param {string} password
   * @returns {Promise<import('../../models/User.js').User>}
   */
  async login(email, password) {
    throw new Error('Método no implementado');
  }

  /**
   * @param {string} email
   * @param {string} password
   * @returns {Promise<import('../../models/User.js').User>}
   */
  async register(email, password) {
    throw new Error('Método no implementado');
  }

  /**
   * @returns {Promise<import('../../models/User.js').User|null>}
   */
  async checkSession() {
    throw new Error('Método no implementado');
  }

  logout() {
    throw new Error('Método no implementado');
  }
}

export class IUserProfileUseCase {
  /**
   * @returns {Promise<import('../../models/User.js').User>}
   */
  async getProfile() {
    throw new Error('Método no implementado');
  }

  /**
   * @param {Object} profileData
   * @returns {Promise<import('../../models/User.js').User>}
   */
  async updateProfile(profileData) {
    throw new Error('Método no implementado');
  }
}
