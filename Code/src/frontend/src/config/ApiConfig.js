/**
 * Configuración centralizada de endpoints y servicios de infraestructura.
 * Separa la configuración del entorno de los adaptadores y servicios.
 */
const isFileProtocol = typeof window !== 'undefined' && window.location.protocol === 'file:';

export const ApiConfig = {
  // En entorno Docker / Nginx se usan rutas relativas '' (proxy reverso integrado sin problemas de CORS).
  // En protocolo file:// o si se especifica en __ENV__, se usan URLs directas.
  FASTAPI_BASE_URL: window.__ENV__?.FASTAPI_URL ?? (isFileProtocol ? 'http://localhost:8000' : ''),
  MICRONAUT_BASE_URL: window.__ENV__?.MICRONAUT_URL ?? (isFileProtocol ? 'http://localhost:8080' : ''),

  endpoints: {
    // Python FastAPI Endpoints (UC-01, UC-02, RF-17 a RF-20)
    predictIntent: '/api/v1/predict/intent',
    healthPython: '/health',
    
    // Java Micronaut Endpoints (UC-09a, UC-09b)
    authLogin: '/api/v1/auth/login',
    authMe: '/api/v1/auth/me',
    registerUser: '/api/v1/users',
    getPortfolio: '/api/v1/portfolio',
    deletePortfolioItem: (ticker) => `/api/v1/portfolio/${encodeURIComponent(ticker)}`,
  },

  timeouts: {
    predict: 15000, // 15s para inferencia de modelos ML
    auth: 8000,
    standard: 5000
  }
};
