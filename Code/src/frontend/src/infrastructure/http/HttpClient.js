/**
 * Cliente HTTP base para infraestructura.
 * Centraliza manejo de cabeceras, serialización JSON, timeouts y captura de errores normalizada.
 */
export class HttpClient {
  /**
   * @param {string} baseUrl
   */
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  /**
   * Ejecuta una petición HTTP genérica.
   * @param {string} path
   * @param {Object} options
   * @returns {Promise<any>}
   */
  async request(path, options = {}) {
    const url = path.startsWith('http') ? path : `${this.baseUrl}${path.startsWith('/') ? '' : '/'}${path}`;
    const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    const controller = new AbortController();
    const timeout = options.timeout || 15000;
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const fetchConfig = {
      method: options.method || 'GET',
      headers,
      signal: controller.signal
    };

    if (options.body && ['POST', 'PUT', 'PATCH'].includes(fetchConfig.method)) {
      fetchConfig.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, fetchConfig);
      clearTimeout(timeoutId);

      let data = null;
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        const errorDetail = data?.detail || data?.message || (typeof data === 'string' ? data : `Error HTTP ${response.status}`);
        const error = new Error(errorDetail);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        const timeoutError = new Error(`Tiempo de espera agotado (${timeout / 1000}s) al conectar con el servidor.`);
        timeoutError.status = 408;
        throw timeoutError;
      }
      throw err;
    }
  }

  get(path, options = {}) {
    return this.request(path, { ...options, method: 'GET' });
  }

  post(path, body, options = {}) {
    return this.request(path, { ...options, method: 'POST', body });
  }

  delete(path, options = {}) {
    return this.request(path, { ...options, method: 'DELETE' });
  }

  put(path, body, options = {}) {
    return this.request(path, { ...options, method: 'PUT', body });
  }
}
