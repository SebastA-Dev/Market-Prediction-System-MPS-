# 🏛️ Frontend NexGenQuant — Arquitectura Hexagonal

Frontend de la plataforma cuantitativa **NexGenQuant**, desarrollado bajo los principios de **Arquitectura Hexagonal (Ports and Adapters)** y desacoplado de frameworks pesados mediante JavaScript ES Modules moderno, Tailwind CSS y Chart.js.

Reproduce fielmente el diseño visual, componentes y experiencia de usuario del MVP especificado en [`Docs/Visual/MVP.html`](../../Docs/Visual/MVP.html).

---

## 📐 Estructura Arquitectónica

```
src/frontend/
├── index.html                   # Entrypoint HTML con estilos Tailwind, FontAwesome y Chart.js
├── package.json                 # Metadatos del proyecto y script de ejecución
├── src/
│   ├── config/
│   │   └── ApiConfig.js         # Configuración centralizada de URLs base y timeouts
│   ├── domain/                  # NÚCLEO DE DOMINIO (Modelos puros y Puertos)
│   │   ├── models/
│   │   │   ├── User.js          # Entidad de usuario y estado de sesión
│   │   │   ├── PortfolioItem.js # Entidad de activo/inversión en seguimiento
│   │   │   ├── Prediction.js    # Entidad de recomendación emitida por el modelo
│   │   │   ├── PredictionIntent.js # Entidad de respuesta analítica (RF-17 a RF-20)
│   │   │   ├── Notification.js  # Entidad de alerta o notificación
│   │   │   └── EducationalTerm.js # Términos del glosario y recursos del Hub Educativo
│   │   └── ports/
│   │       ├── in/              # PUERTOS DE ENTRADA (Casos de Uso)
│   │       │   ├── IPredictIntentUseCase.js
│   │       │   ├── IPortfolioUseCases.js
│   │       │   ├── IAuthUseCases.js
│   │       │   └── INotificationsUseCases.js
│   │       └── out/             # PUERTOS DE SALIDA (Contratos para Sistemas Externos)
│   │           ├── IPredictionRepositoryPort.js
│   │           ├── IPortfolioRepositoryPort.js
│   │           ├── IAuthRepositoryPort.js
│   │           └── INotificationAndStoragePorts.js
│   ├── application/             # SERVICIOS DE APLICACIÓN (Implementación de Casos de Uso)
│   │   ├── PredictIntentService.js
│   │   ├── PortfolioApplicationService.js
│   │   ├── AuthApplicationService.js
│   │   ├── NotificationApplicationService.js
│   │   └── UserProfileApplicationService.js
│   ├── infrastructure/          # INFRAESTRUCTURA (Adaptadores de Entrada y Salida)
│   │   ├── http/
│   │   │   └── HttpClient.js    # Cliente Fetch base con control de errores y timeouts
│   │   ├── adapters/
│   │   │   ├── out/             # ADAPTADORES SECUNDARIOS (Llamadas a Backend y Storage)
│   │   │   │   ├── FastApiPredictionAdapter.js  # FastAPI Python (Puerto 8000)
│   │   │   │   ├── MicronautPortfolioAdapter.js # Micronaut Java (Puerto 8080)
│   │   │   │   ├── MicronautAuthAdapter.js      # Micronaut Java (Puerto 8080)
│   │   │   │   ├── NotificationRestAdapter.js   # Alertas y notificaciones
│   │   │   │   └── BrowserStorageAdapter.js     # Persistencia localStorage
│   │   │   └── in/              # ADAPTADORES PRIMARIOS (Estado y Controladores)
│   │   │       ├── state/
│   │   │       │   └── AppState.js              # Gestor de estado reactivo observable
│   │   │       └── controllers/
│   │   │           ├── AdvisorController.js     # Controlador del Consejero IA
│   │   │           ├── PortfolioController.js   # Controlador de inversiones
│   │   │           ├── AuthController.js        # Controlador de autenticación
│   │   │           └── NotificationController.js# Controlador de notificaciones
│   └── ui/                      # CAPA DE PRESENTACIÓN (Vistas, Componentes y Gráficos)
│       ├── components/
│       │   ├── HeaderComponent.js
│       │   ├── SearchPromptComponent.js
│       │   ├── LoadingComponent.js
│       │   ├── ResultsComponent.js
│       │   ├── TrustDrawerComponent.js
│       │   ├── UserModalComponent.js
│       │   ├── EducationalGuideComponent.js
│       │   └── ToastComponent.js
│       ├── charts/
│       │   └── ChartManager.js  # Gestión de ciclo de vida seguro de Chart.js (RF-43)
│       └── app.js               # Inyección de dependencias y bootstrap de la app
```

---

## 🔗 Matriz de Integración con Endpoints del Backend

| Funcionalidad | Método | Endpoint Backend | Microservicio | Adaptador Hexagonal | Estado |
|---|---|---|---|---|---|
| **Clasificación de Intención y Predicción** | `POST` | `/api/v1/predict/intent` | Python (FastAPI :8000) | `FastApiPredictionAdapter` | ✅ **Conectado** |
| **Inicio de Sesión (JWT)** | `POST` | `/api/v1/auth/login` | Java (Micronaut :8080) | `MicronautAuthAdapter` | ✅ **Conectado** |
| **Registro de Usuario (UUID)** | `POST` | `/api/v1/users` | Java (Micronaut :8080) | `MicronautAuthAdapter` | ✅ **Conectado** |
| **Validar Sesión Activa** | `GET` | `/api/v1/auth/me` | Java (Micronaut :8080) | `MicronautAuthAdapter` | ✅ **Conectado** |
| **Consultar Portafolio de Inversiones** | `GET` | `/api/v1/portfolio` | Java (Micronaut :8080) | `MicronautPortfolioAdapter` | ✅ **Conectado** |
| **Eliminar Inversión de Portafolio** | `DELETE` | `/api/v1/portfolio/{ticker}` | Java (Micronaut :8080) | `MicronautPortfolioAdapter` | ✅ **Conectado** |
| **Guardar Inversión en Portafolio** | `POST` | *(Pendiente en Backend)* | Java (Micronaut :8080) | `MicronautPortfolioAdapter` | ⏳ **Marcador TODO** |
| **Consultar Historial de Alertas** | `GET` | *(Pendiente en Backend)* | Java (Micronaut :8080) | `NotificationRestAdapter` | ⏳ **Marcador TODO** |
| **Limpiar Notificaciones** | `DELETE` | *(Pendiente en Backend)* | Java (Micronaut :8080) | `NotificationRestAdapter` | ⏳ **Marcador TODO** |
| **Actualizar Perfil de Usuario** | `PUT` | *(Pendiente en Backend)* | Java (Micronaut :8080) | `MicronautAuthAdapter` | ⏳ **Marcador TODO** |

---

## 📌 Identificación de Endpoints Pendientes (Marcadores TODO)

Siguiendo la restricción estricta de **no inventar URLs ni simular integraciones falsas**, las funcionalidades cuyos endpoints aún no existen en el backend contienen el marcador exacto:

```javascript
// TODO: Colocar URL hacia el endpoint
```

1. **`MicronautPortfolioAdapter.js` — Guardar inversión en portafolio**:
   - Marcador: `// TODO: Colocar URL hacia el endpoint`
   - Método HTTP esperado: `POST`
   - Propósito: Suscribir/agregar activo al portafolio en PostgreSQL (`user_configuration`) para el usuario autenticado (UC-09b, RF-22).

2. **`NotificationRestAdapter.js` — Historial de alertas**:
   - Marcador: `// TODO: Colocar URL hacia el endpoint`
   - Método HTTP esperado: `GET`
   - Propósito: Consultar registros de la tabla `alert_history` en PostgreSQL (UC-10, RF-27).

3. **`NotificationRestAdapter.js` — Limpiar alertas**:
   - Marcador: `// TODO: Colocar URL hacia el endpoint`
   - Método HTTP esperado: `DELETE` o `POST`
   - Propósito: Marcar como leídas o borrar alertas del usuario.

4. **`MicronautAuthAdapter.js` — Actualización de perfil**:
   - Marcador: `// TODO: Colocar URL hacia el endpoint`
   - Método HTTP esperado: `PUT` o `PATCH`
   - Propósito: Modificar nombre y perfil de riesgo del usuario en la base de datos relacional.

---

## 🚀 Cómo Ejecutar el Frontend

1. Abrir `index.html` directamente en el navegador, o
2. Servir con cualquier servidor HTTP local:
   ```bash
   cd Code/src/frontend
   npx serve -l 3000 .
   ```
   o con Python:
   ```bash
   cd Code/src/frontend
   python -m http.server 3000
   ```
3. Abrir `http://localhost:3000`.
