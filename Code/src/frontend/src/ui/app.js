// ==============================================================================
// 1. Capa de Infraestructura (Adaptadores de Salida y HTTP)
// ==============================================================================
import { FastApiPredictionAdapter } from '../infrastructure/adapters/out/FastApiPredictionAdapter.js';
import { MicronautPortfolioAdapter } from '../infrastructure/adapters/out/MicronautPortfolioAdapter.js';
import { MicronautAuthAdapter } from '../infrastructure/adapters/out/MicronautAuthAdapter.js';
import { NotificationRestAdapter } from '../infrastructure/adapters/out/NotificationRestAdapter.js';
import { BrowserStorageAdapter } from '../infrastructure/adapters/out/BrowserStorageAdapter.js';

// ==============================================================================
// 2. Capa de Aplicación (Casos de Uso)
// ==============================================================================
import { PredictIntentService } from '../application/PredictIntentService.js';
import { PortfolioApplicationService } from '../application/PortfolioApplicationService.js';
import { AuthApplicationService } from '../application/AuthApplicationService.js';
import { NotificationApplicationService } from '../application/NotificationApplicationService.js';
import { UserProfileApplicationService } from '../application/UserProfileApplicationService.js';

// ==============================================================================
// 3. Capa de Infraestructura (Adaptadores de Entrada: Estado y Controladores)
// ==============================================================================
import { globalAppState } from '../infrastructure/adapters/in/state/AppState.js';
import { AdvisorController } from '../infrastructure/adapters/in/controllers/AdvisorController.js';
import { PortfolioController } from '../infrastructure/adapters/in/controllers/PortfolioController.js';
import { AuthController } from '../infrastructure/adapters/in/controllers/AuthController.js';
import { NotificationController } from '../infrastructure/adapters/in/controllers/NotificationController.js';

// ==============================================================================
// 4. Capa de Presentación (Componentes de Interfaz de Usuario)
// ==============================================================================
import { HeaderComponent } from './components/HeaderComponent.js';
import { SearchPromptComponent } from './components/SearchPromptComponent.js';
import { LoadingComponent } from './components/LoadingComponent.js';
import { ResultsComponent } from './components/ResultsComponent.js';
import { TrustDrawerComponent } from './components/TrustDrawerComponent.js';
import { UserModalComponent } from './components/UserModalComponent.js';
import { EducationalGuideComponent } from './components/EducationalGuideComponent.js';
import { ToastComponent } from './components/ToastComponent.js';

/**
 * Contenedor de Inyección de Dependencias y Coordinador de la Aplicación Frontend.
 * Respeta rigurosamente la Arquitectura Hexagonal (Puertos y Adaptadores).
 */
class AppBootstrap {
  constructor() {
    // 1. Instanciación de Adaptadores Secundarios (Outbound Adapters)
    this.storageAdapter = new BrowserStorageAdapter();
    this.predictionAdapter = new FastApiPredictionAdapter();
    this.portfolioAdapter = new MicronautPortfolioAdapter();
    this.authAdapter = new MicronautAuthAdapter();
    this.notificationAdapter = new NotificationRestAdapter();

    // 2. Instanciación de Servicios de Aplicación (Casos de Uso)
    this.predictService = new PredictIntentService(this.predictionAdapter);
    this.portfolioService = new PortfolioApplicationService(this.portfolioAdapter, this.storageAdapter);
    this.authService = new AuthApplicationService(this.authAdapter, this.storageAdapter);
    this.userProfileService = new UserProfileApplicationService(this.authAdapter, this.storageAdapter);
    this.notificationService = new NotificationApplicationService(this.notificationAdapter, this.storageAdapter);

    // 3. Instanciación de Controladores Primarios (Inbound Adapters)
    this.advisorController = new AdvisorController(this.predictService, this.portfolioService);
    this.portfolioController = new PortfolioController(this.portfolioService);
    this.authController = new AuthController(this.authService, this.userProfileService, this.portfolioService);
    this.notificationController = new NotificationController(this.notificationService);

    // 4. Instanciación de Componentes de Interfaz
    this.headerComponent = new HeaderComponent({
      advisor: this.advisorController,
      notification: this.notificationController,
      portfolio: this.portfolioController
    });
    this.searchPromptComponent = new SearchPromptComponent(this.advisorController);
    this.loadingComponent = new LoadingComponent();
    this.resultsComponent = new ResultsComponent(this.advisorController);
    this.trustDrawerComponent = new TrustDrawerComponent(this.advisorController);
    this.userModalComponent = new UserModalComponent({
      portfolio: this.portfolioController,
      auth: this.authController
    });
    this.educationalGuideComponent = new EducationalGuideComponent();
    this.toastComponent = new ToastComponent();

    this.rootEl = document.getElementById('app-root');
  }

  init() {
    if (!this.rootEl) {
      console.error('No se encontró el elemento raíz #app-root');
      return;
    }

    // Suscripción reactiva al estado global
    globalAppState.subscribe((state) => {
      this.render(state);
    });

    // Cargar sesión inicial y datos base
    this.authController.initSession();
    this.notificationController.loadNotifications();

    // Render inicial
    this.render(globalAppState.get());
  }

  render(state) {
    const isAdvisor = state.currentView === 'advisor';

    this.rootEl.innerHTML = `
      ${this.headerComponent.render(state)}

      <main class="flex-grow pt-20 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full flex flex-col items-center">
        ${
          isAdvisor
            ? `
              <div id="advisor-view" class="w-full flex flex-col items-center">
                ${this.searchPromptComponent.render(state)}
                ${this.loadingComponent.render(state)}
                ${this.resultsComponent.render(state)}
              </div>
            `
            : this.educationalGuideComponent.render(state)
        }
      </main>

      ${this.trustDrawerComponent.render(state)}
      ${this.userModalComponent.render(state)}
      ${this.toastComponent.render(state)}
    `;

    // Vincular controladores a los eventos del DOM
    this.attachEvents(state);
  }

  attachEvents(state) {
    this.headerComponent.attachEvents(this.rootEl);
    this.searchPromptComponent.attachEvents(this.rootEl);
    this.resultsComponent.attachEvents(this.rootEl, state);
    this.trustDrawerComponent.attachEvents(this.rootEl);
    this.userModalComponent.attachEvents(this.rootEl);
    this.educationalGuideComponent.attachEvents(this.rootEl);
  }
}

// Iniciar aplicación al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
  const app = new AppBootstrap();
  app.init();
});
