import { IAuthRepositoryPort } from '../../../domain/ports/out/IAuthRepositoryPort.js';
import { ApiConfig } from '../../../config/ApiConfig.js';
import { HttpClient } from '../../http/HttpClient.js';

/**
 * Adaptador Secundario (Outbound Adapter): MicronautAuthAdapter
 * Conecta el frontend con los endpoints de identidad y seguridad de Micronaut.
 */
export class MicronautAuthAdapter extends IAuthRepositoryPort {
  /**
   * @param {HttpClient} [httpClient]
   */
  constructor(httpClient = null) {
    super();
    this.http = httpClient || new HttpClient(ApiConfig.MICRONAUT_BASE_URL);
  }

  /**
   * Inicia sesión verificando credenciales PBKDF2 y obteniendo token JWT.
   * Conectado a POST /api/v1/auth/login.
   * @param {string} email
   * @param {string} password
   */
  async login(email, password) {
    return await this.http.post(ApiConfig.endpoints.authLogin, {
      email,
      password
    });
  }

  /**
   * Registra un nuevo usuario con UUID v4 en la base de datos relacional.
   * Conectado a POST /api/v1/users.
   * @param {string} email
   * @param {string} password
   */
  async register(email, password) {
    return await this.http.post(ApiConfig.endpoints.registerUser, {
      email,
      password
    });
  }

  /**
   * Valida la identidad del token JWT.
   * Conectado a GET /api/v1/auth/me.
   * @param {string} token
   */
  async getMe(token) {
    return await this.http.get(ApiConfig.endpoints.authMe, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }

  /**
   * Actualiza la información de perfil y perfil de riesgo del usuario.
   * Estructura preparada bajo arquitectura hexagonal para la posterior integración con el backend.
   * 
   * Método HTTP esperado: PUT o PATCH
   * Propósito: Actualizar el nombre completo y perfil de riesgo del usuario en la base de datos.
   * 
   * @param {string} token
   * @param {Object} profileData
   */
  async updateProfile(token, profileData) {
    // TODO: Colocar URL hacia el endpoint
    // Método esperado: PUT o PATCH
    // Propósito: Actualizar nombre y preferencias de riesgo del usuario autenticado
    const endpointUrl = null; // Pendiente de implementación en el backend

    if (!endpointUrl) {
      return profileData;
    }

    return await this.http.put(endpointUrl, profileData, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }
}
