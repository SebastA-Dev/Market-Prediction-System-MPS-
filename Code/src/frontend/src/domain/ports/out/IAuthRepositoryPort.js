/**
 * Puerto de Salida (Outbound Port): IAuthRepositoryPort
 * Contrato para acceder al servicio de autenticación y gestión de usuarios (Micronaut).
 */
export class IAuthRepositoryPort {
  /**
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{token: string, tokenType: string, expiresIn: number, user: Object}>}
   */
  async login(email, password) {
    throw new Error('Método no implementado');
  }

  /**
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{id: string, email: string, createdAt: string}>}
   */
  async register(email, password) {
    throw new Error('Método no implementado');
  }

  /**
   * @param {string} token
   * @returns {Promise<{id: string, email: string}>}
   */
  async getMe(token) {
    throw new Error('Método no implementado');
  }

  /**
   * @param {string} token
   * @param {Object} profileData
   * @returns {Promise<Object>}
   */
  async updateProfile(token, profileData) {
    throw new Error('Método no implementado');
  }
}
