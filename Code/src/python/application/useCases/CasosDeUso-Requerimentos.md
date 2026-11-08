# Especificación de Requerimientos y Casos de uso del Sistema

## Plataforma Cuantitativa de Inversión Predictiva

**Base:** Backlog de Historias de Usuario (4 épicas, 18 historias)

**Convención de ID:**

- `RF-XX`: Requerimientos Funcionales (numeración continua, agrupada por módulo).
- `RNF-XX`: Requerimientos No Funcionales (numeración continua, clasificada según estándares de calidad ISO/IEC 25010).
  **Trazabilidad:** Cada ítem referencia explícitamente las historias de usuario de origen y los componentes técnicos involucrados.

---

# 1. Requerimientos Funcionales (RF)

## Módulo 1 — Ingesta y Procesamiento de Datos en Streaming (Python)

**RF-01.** El sistema deberá recibir ticks de mercado en tiempo real mediante una conexión WebSocket persistente con el proveedor de datos externo.

_(Fuente: HU-1.1)_

**RF-02.** El sistema deberá encolar cada tick recibido en una estructura de datos en memoria (`asyncio.Queue`) en un tiempo menor a 10 ms desde su recepción.

_(Fuente: HU-1.1)_

**RF-03.** El sistema deberá reintentar automáticamente la conexión WebSocket con el proveedor de datos ante una caída, mediante una estrategia de backoff exponencial, sin detener el proceso completo.

_(Fuente: HU-1.1)_

**RF-04.** El sistema deberá descartar y registrar en log cualquier tick recibido con formato inválido, sin interrumpir el pipeline de procesamiento.

_(Fuente: HU-1.1)_

**RF-05.** El sistema deberá transformar los ticks crudos en vectores de Alpha Factors mediante el framework Qlib, persistiendo el resultado en su formato binario nativo.

_(Fuente: HU-1.2)_

**RF-06.** El sistema deberá retornar un estado de "datos insuficientes" cuando existan menos de 30 observaciones históricas disponibles para un ticker, en lugar de ejecutar el cálculo de Alpha Factors.

_(Fuente: HU-1.2)_

**RF-07.** El sistema deberá ejecutar el modelo MASTER sobre los Alpha Factors de múltiples activos, generando una predicción de tendencia por activo junto con su score de correlación inter-sectorial.

_(Fuente: HU-1.3)_

**RF-08.** El sistema deberá ejecutar el modelo Galformer sobre la serie temporal de un activo individual, generando una predicción puntual de tendencia con su horizonte temporal asociado.

_(Fuente: HU-1.4)_

**RF-09.** El sistema deberá aplicar una prueba de hipótesis estadística (Z-test) con nivel de significancia $\alpha = 0.05$ sobre cada predicción generada.

_(Fuente: HU-1.5)_

**RF-10.** El sistema deberá emitir una señal `BUY` o `SELL`, junto con su p-value, únicamente cuando el valor absoluto del z-score supere el z crítico de 1.96.

_(Fuente: HU-1.5)_

**RF-11.** El sistema deberá emitir una señal `HOLD` y omitir la publicación de cualquier evento cuando el z-score se encuentre dentro del rango $[-1.96, 1.96]$.

_(Fuente: HU-1.5)_

**RF-12.** El sistema deberá retornar una señal `HOLD` sin generar error cuando la desviación estándar del histórico de precios sea igual a cero.

_(Fuente: HU-1.5)_

**RF-13.** El sistema deberá publicar cada señal validada ($p < 0.05$) en el canal Redis `market_signals`, con el payload `{ticker, price, signal, p_value}`, en un tiempo menor a 100 ms desde la recepción del tick original.

_(Fuente: HU-1.6)_

**RF-14.** El sistema deberá registrar en log cualquier fallo de publicación hacia Redis sin bloquear el procesamiento de nuevos ticks entrantes.

_(Fuente: HU-1.6)_

**RF-15.** El sistema deberá insertar en la colección `market_ticks_and_features` de MongoDB un documento por cada tick procesado, incluyendo ticks crudos, Alpha Factors, inferencias de MASTER y Galformer, p-value y marca temporal — haya o no señal significativa.

_(Fuente: HU-1.7)_

**RF-16.** El sistema deberá garantizar que la colección `market_ticks_and_features` opere bajo un patrón append-only, sin permitir operaciones de actualización o eliminación sobre los documentos existentes.

_(Fuente: HU-1.7)_

**RF-17.** El sistema deberá exponer un endpoint `POST /api/v1/predict/intent` que reciba un prompt en texto plano y lo clasifique en una de las categorías `INTENT_MACRO`, `INTENT_SECTORIAL` o `INTENT_ACTIVO`.

_(Fuente: HU-1.8)_

**RF-18.** El sistema deberá retornar, para un prompt clasificado como `INTENT_MACRO`, una distribución de capital sugerida a nivel de mercado general.

_(Fuente: HU-1.8)_

**RF-19.** El sistema deberá retornar, para un prompt clasificado como `INTENT_SECTORIAL`, un conjunto de activos pertenecientes al sector identificado en el prompt.

_(Fuente: HU-1.8)_

**RF-20.** El sistema deberá solicitar una aclaración al usuario, en lugar de retornar un error HTTP 500, cuando el prompt recibido no pueda ser clasificado en ninguna de las categorías de intención soportadas.

_(Fuente: HU-1.8)_

---

## Módulo 2 — Gestión de Usuarios y Alertas (Java)

**RF-21.** El sistema deberá permitir el registro de un nuevo usuario mediante un correo electrónico válido, generando un identificador único (UUID) para cada registro.

_(Fuente: HU-2.1)_

**RF-22.** El sistema deberá permitir a un usuario registrado configurar un ticker de interés (`target_ticker`) y activar o desactivar la recepción de alertas (`alerts_enabled`), persistiendo dicha configuración.

_(Fuente: HU-2.1)_

**RF-23.** El sistema deberá suscribirse al canal Redis `market_signals` para recibir de forma reactiva las señales publicadas por el contexto analítico.

_(Fuente: HU-2.2)_

**RF-24.** El sistema deberá evaluar cada señal entrante contra las configuraciones activas de los usuarios, notificando únicamente cuando el ticker de la señal coincida con el `target_ticker` configurado y `alerts_enabled` sea verdadero.

_(Fuente: HU-2.2)_

**RF-25.** El sistema deberá omitir la generación de notificación e historial cuando la configuración del usuario tenga `alerts_enabled` en falso, o cuando el ticker de la señal no coincida con su configuración.

_(Fuente: HU-2.2)_

**RF-26.** El sistema deberá insertar un registro en `alert_history` (`ticker`, `price`, `triggered_at`) cada vez que se dispare una alerta válida para un usuario.

_(Fuente: HU-2.3)_

**RF-27.** El sistema deberá permitir a un usuario consultar su historial de alertas, retornando los registros ordenados de forma descendente por fecha de disparo.

_(Fuente: HU-2.3)_

**RF-28.** El sistema deberá garantizar que el paquete `domain` de la aplicación Java no dependa de ninguna librería de infraestructura (Micronaut, JPA, Jackson, Redis).

_(Fuente: HU-2.4)_

**RF-29.** El sistema deberá permitir la ejecución completa de las pruebas unitarias de la lógica de negocio (`SignalNotificationService`) utilizando exclusivamente repositorios _fake_ en memoria, sin requerir PostgreSQL ni Redis en ejecución.

_(Fuente: HU-2.4)_

---

## Módulo 3 — Interfaz Conversacional Basada en Intenciones (Frontend)

**RF-30.** El sistema deberá proveer una barra de búsqueda principal que reciba una intención de inversión escrita en lenguaje natural.

_(Fuente: HU-3.1)_

**RF-31.** El sistema deberá renderizar la vista de asignación macro/diversificada cuando el prompt del usuario contenga un monto sin especificar sector o activo.

_(Fuente: HU-3.1)_

**RF-32.** El sistema deberá renderizar la vista de activos de un sector cuando el prompt del usuario contenga un monto junto con un sector explícito.

_(Fuente: HU-3.1)_

**RF-33.** El sistema deberá renderizar la vista de análisis individual cuando el prompt del usuario contenga el nombre de un activo específico.

_(Fuente: HU-3.1)_

**RF-34.** El sistema deberá mostrar un elemento interactivo ("¿Por qué?") que, al ser activado, despliegue una explicación en lenguaje simple sobre la tendencia detectada y la consistencia de la evidencia estadística.

_(Fuente: HU-3.2)_

**RF-35.** El sistema deberá generar todo texto explicativo de recomendaciones utilizando lenguaje condicional/probabilístico, sin incluir en ningún caso verbos en futuro categórico (p. ej. "subirá", "ganarás").

_(Fuente: HU-3.2)_

**RF-36.** El sistema deberá mostrar, junto a cada indicador de confianza, un texto aclaratorio explícito indicando que dicho indicador representa la consistencia de la evidencia estadística y no la probabilidad de obtener ganancias.

_(Fuente: HU-3.3)_

**RF-37.** El sistema deberá incluir, en toda vista de recomendación de tipo macro o sectorial, un bloque de contexto macroeconómico con tendencias generales y riesgos asociados.

_(Fuente: HU-3.4)_

**RF-38.** El sistema deberá renderizar un gráfico de distribución porcentual de capital entre activos/sectores para cada recomendación generada a partir de un monto ingresado.

_(Fuente: HU-3.5)_

**RF-39.** El sistema deberá permitir al usuario ajustar manualmente los porcentajes del gráfico de distribución de capital, recalculando y re-renderizando el gráfico con el nuevo escenario.

_(Fuente: HU-3.5)_

**RF-40.** El sistema deberá mostrar, para cada activo recomendado, niveles sugeridos de stop-loss y take-profit acompañados de una breve explicación de su significado.

_(Fuente: HU-3.6)_

**RF-41.** El sistema deberá proveer un panel de Hub Educativo accesible desde cualquier vista de la aplicación, que permita buscar y navegar definiciones de conceptos clave sin interrumpir el flujo principal.

_(Fuente: HU-3.7)_

**RF-42.** El sistema deberá abrir la definición correspondiente en el Hub Educativo cuando el usuario haga clic sobre un término técnico resaltado dentro de una recomendación.

_(Fuente: HU-3.7)_

**RF-43.** El sistema deberá destruir toda instancia previa de gráficos Chart.js antes de renderizar una nueva vista, para prevenir fugas de memoria y congelamiento del navegador.

_(Fuente: HU-3.8)_

**RF-44.** El sistema deberá reemplazar los datos simulados del prototipo por llamadas reales al endpoint `POST /api/v1/predict/intent`, renderizando la respuesta obtenida del backend.

_(Fuente: HU-3.9)_

**RF-45.** El sistema deberá mostrar un estado de error legible en el frontend cuando la llamada al backend falle o exceda el tiempo de espera, en lugar de mantener un estado de carga indefinido.

_(Fuente: HU-3.9)_

---

## Módulo 4 — Infraestructura y Despliegue (Transversal)

**RF-46.** El sistema deberá permitir el despliegue simultáneo de FastAPI, Redis, PostgreSQL y MongoDB mediante un único archivo de orquestación (`docker-compose.yml`), quedando todos los servicios disponibles y saludables tras su ejecución.

_(Fuente: HU-4.1)_

**RF-47.** El sistema deberá establecer conexión entre el servicio Java y PostgreSQL de forma automática dentro del entorno orquestado, sin requerir configuración manual adicional.

_(Fuente: HU-4.1)_

**RF-48.** El sistema deberá implementar el adaptador `PostgresSignalRepository` mediante Micronaut Data, persistiendo cada señal procesada y válida en la tabla `alert_history` de PostgreSQL.

_(Fuente: HU-4.2)_

**RF-49.** El sistema deberá garantizar que los tests unitarios de dominio existentes (basados en repositorios fake) continúen pasando sin modificación tras la incorporación del adaptador real de persistencia.

_(Fuente: HU-4.2)_

---

## Trazabilidad Resumida de Requerimientos Funcionales

| Módulo                                         | Rango RF      | Historias de Usuario Cubiertas                                         |
| ---------------------------------------------- | ------------- | ---------------------------------------------------------------------- |
| **Ingesta y Procesamiento (Python)**           | RF-01 a RF-20 | HU-1.1, HU-1.2, HU-1.3, HU-1.4, HU-1.5, HU-1.6, HU-1.7, HU-1.8         |
| **Gestión de Usuarios y Alertas (Java)**       | RF-21 a RF-29 | HU-2.1, HU-2.2, HU-2.3, HU-2.4                                         |
| **Interfaz Conversacional (Frontend)**         | RF-30 a RF-45 | HU-3.1, HU-3.2, HU-3.3, HU-3.4, HU-3.5, HU-3.6, HU-3.7, HU-3.8, HU-3.9 |
| **Infraestructura y Despliegue (Transversal)** | RF-46 a RF-49 | HU-4.1, HU-4.2                                                         |

_Total de Requerimientos Funcionales: 49_

---

# 2. Requerimientos No Funcionales (RNF)

## Rendimiento, Eficiencia y Capacidad

**RNF-01 (Latencia de Ingesta en Memoria):**

El tiempo de procesamiento transcurrido desde la recepción física del tick vía WebSocket hasta su encolado en memoria (`asyncio.Queue`) no debe superar los 10 ms bajo condiciones normales de carga.

_(Módulo: Python / HU-1.1)_

**RNF-02 (Latencia End-to-End del Pipeline Analítico):**

El tiempo total transcurrido desde la llegada de un tick al pipeline hasta la emisión efectiva de la señal validada en el canal Redis `market_signals` no debe exceder los 100 ms.

_(Módulo: Python / HU-1.6)_

**RNF-03 (Tiempo de Respuesta del Clasificador Conversacional):**

El endpoint `POST /api/v1/predict/intent` debe retornar la respuesta procesada en un percentil 95 (P95) inferior a 1.5 segundos ante consultas en lenguaje natural en entornos de producción.

_(Módulo: Python / HU-1.8, HU-3.9)_

**RNF-04 (Rendimiento de Evaluación de Alertas Reactivas):**

El motor reactivo en Java debe evaluar una señal entrante contra un volumen de al menos 1,000 suscripciones de usuario activas en memoria en un tiempo menor a 50 ms.

_(Módulo: Java / HU-2.2)_

**RNF-05 (Rendimiento de Inserción en Base Documental):**

La base de datos MongoDB debe estar optimizada mediante índices compuestos en `{ticker: 1, timestamp: -1}` para soportar un régimen de escritura continuo de al menos 500 documentos por segundo sin degradar el pipeline de ingesta.

_(Módulo: Python / HU-1.7)_

**RNF-06 (Tiempo de Carga y Rendimiento Web):**

El paquete inicial de JavaScript del frontend no debe superar los 350 KB transferidos (comprimido vía Gzip o Brotli), logrando un _First Contentful Paint_ (FCP) inferior a 1.2 segundos y un _Largest Contentful Paint_ (LCP) inferior a 2.5 segundos.

_(Módulo: Frontend / HU-3.1)_

---

## Confiabilidad, Resiliencia y Manejo de Sobrecarga (Backpressure)

**RNF-07 (Reconexión Resiliente con Backoff Exponencial):**

Ante caídas del enlace WebSocket externo, el sistema debe reintentar la conexión automáticamente aplicando backoff exponencial con _jitter_ (factores entre 1s y 60s), evitando la saturación del event loop y la terminación del proceso.

_(Módulo: Python / HU-1.1)_

**RNF-08 (Control de Concurrencia y Bounded Queue):**

La cola interna en memoria (`asyncio.Queue`) en el servicio de ingesta debe tener una capacidad máxima acotada a 5,000 eventos. Ante picos de volatilidad donde el flujo supere la velocidad de inferencia, se debe aplicar descarte selectivo de ticks antiguos (_drop oldest_) registrando el incidente en logs, evitando fallos por falta de memoria (OOM).

_(Módulo: Python / HU-1.1, HU-1.2)_

**RNF-09 (Aislamiento de Fallos en Mensajería Redis):**

Fallas temporales de red o indisponibilidad en el canal Redis `market_signals` deben ser capturadas y registradas en logs sin suspender, degradar ni bloquear la recepción y procesamiento de ticks entrantes en el worker principal.

_(Módulo: Python / HU-1.6)_

**RNF-10 (Expiración de Mensajes y Prevención de Señales Obsoletas):**

El broker Redis debe configurar una política de expiración o tiempo de vida (TTL) de mensaje no superior a 5 minutos sobre las señales publicadas. Al reconectarse el consumidor Java, este no debe procesar señales históricas obsoletas acumuladas durante la caída.

_(Módulo: Transversal / HU-1.6, HU-2.2)_

**RNF-11 (Degradación Determinista por Insuficiencia de Datos):**

Cuando un activo posea menos de 30 observaciones históricas o su desviación estándar sea igual a cero, el pipeline debe degradar a un estado controlado (`HOLD` o datos insuficientes), inhibiendo cálculos estadísticos y previniendo excepciones aritméticas no controladas (como división por cero).

_(Módulo: Python / HU-1.2, HU-1.5)_

**RNF-12 (Inmutabilidad de Registros Analíticos):**

La colección `market_ticks_and_features` en MongoDB debe operar bajo una política estricta de sólo adición (_append-only_), restringiendo operaciones de modificación (`update`) o borrado (`delete`) a nivel de aplicación para garantizar la auditabilidad retrospectiva.

_(Módulo: Python / HU-1.7)_

---

## Arquitectura, Mantenibilidad y Calidad de Código

**RNF-13 (Aislamiento de Dominio - Arquitectura Hexagonal):**

El módulo `domain` en el servicio Java debe mantenerse desacoplado y completamente agnóstico de frameworks y dependencias de infraestructura (Micronaut Data, JPA, Jackson, Redis), permitiendo su portabilidad e independencia tecnológica.

_(Módulo: Java / HU-2.4)_

**RNF-14 (Testabilidad Unitaria sin Infraestructura):**

La suite completa de pruebas unitarias del servicio de notificaciones (`SignalNotificationService`) debe ejecutarse en memoria en menos de 2 segundos empleando dobles de prueba (_fakes_), sin depender de instancias activas de PostgreSQL ni de Redis.

_(Módulo: Java / HU-2.4, HU-4.2)_

**RNF-15 (Estandarización de Interfaz RESTful):**

El endpoint conversacional debe ajustarse a las convenciones REST, retornando respuestas estructuradas en formato JSON y códigos de estado semánticos: `200 OK` (éxito), `400 Bad Request` con payload de clarificación (intención no interpretable) y `503 Service Unavailable` (indisponibilidad de servicios).

_(Módulo: Python / HU-1.8, HU-3.9)_

**RNF-16 (Gestión del Ciclo de Vida en DOM y Gráficos):**

El frontend debe destruir explícitamente la instancia previa de Chart.js antes de renderizar un nuevo escenario en el canvas, previniendo fugas de memoria, listeners zombis y congelamiento de interfaz durante transiciones de vistas.

_(Módulo: Frontend / HU-3.8)_

**RNF-17 (Pool de Conexiones Relacionales):**

El microservicio en Java debe interactuar con PostgreSQL a través de un pool de conexiones optimizado (HikariCP) con un límite máximo de 20 conexiones simultáneas y un tiempo de espera de adquisición (_connection timeout_) no superior a 250 ms.

_(Módulo: Java / HU-4.2)_

**RNF-18 (Apagado Seguro de Procesos - Graceful Shutdown):**

Al recibir señales de terminación del sistema operativo (`SIGTERM` o `SIGINT`), los servicios de backend deben contar con un periodo de gracia de hasta 15 segundos para vaciar buffers en memoria, completar transacciones en curso y liberar conexiones a Redis y bases de datos.

_(Módulo: Transversal / HU-4.1)_

---

## Reglas de Negocio, Ética y Mitigación de Riesgo Legal

**RNF-19 (Lenguaje Estrictamente Condicional y Probabilístico):**

Ningún texto explicativo o recomendación generada por la plataforma podrá redactarse con verbos en futuro categórico (ej. "el activo subirá", "ganarás"). Todas las descripciones analíticas deben expresarse obligatoriamente en términos probabilísticos o escenarios condicionales.

_(Módulo: Frontend / HU-3.2)_

**RNF-20 (Transparencia Legal del Indicador de Confianza):**

El sistema debe exhibir permanentemente un texto visible junto al indicador de confianza aclarando que este representa la consistencia y significancia de la evidencia estadística matemática (nivel de p-value), y bajo ningún concepto traduce una probabilidad de rentabilidad monetaria o garantía de retorno.

_(Módulo: Frontend / HU-3.3)_

**RNF-21 (Prohibición de Datos Simulados en Producción):**

Queda terminantemente prohibido el despliegue de datos simulados (_mocks_) o valores cableados en el entorno productivo; toda asignación de capital, activo o contexto desplegado al usuario debe provenir del pipeline analítico real (Qlib + MASTER + Galformer).

_(Módulo: Frontend / HU-3.9)_

**RNF-22 (Integridad en Distribución de Capital):**

El mecanismo de ajuste interactivo de asignación de capital debe validar que la sumatoria de las participaciones porcentuales asignadas a sectores o activos totalice exactamente el 100%, bloqueando o recalculando automáticamente escenarios inconsistentes.

_(Módulo: Frontend / HU-3.5)_

---

## Seguridad, Privacidad y Cumplimiento

**RNF-23 (Identificadores Opacos Criptográficos):**

La identificación de entidades de usuario en la capa de persistencia debe realizarse mediante Identificadores Únicos Universales (UUID v4) generados criptográficamente, previniendo ataques de enumeración o inferencia de volumen de usuarios.

_(Módulo: Java / HU-2.1)_

**RNF-24 (Sanitización y Validación de Entradas):**

El endpoint de procesamiento de lenguaje natural debe sanear y normalizar todo texto de entrada, mitigando vectores de inyección de código, desbordamientos de buffer y secuencias malformadas de caracteres Unicode/UTF-8.

_(Módulo: Python / HU-1.8)_

**RNF-25 (Cifrado de Tráfico en Tránsito):**

Todas las comunicaciones externas de la plataforma deben exigir canales cifrados seguros bajo TLS 1.3: `WSS://` para el flujo continuo de cotizaciones y `HTTPS://` para la interacción cliente-servidor y endpoints analíticos.

_(Módulo: Transversal / HU-1.1, HU-3.9)_

**RNF-26 (Protección de Datos Personales en Reposo):**

Las direcciones de correo electrónico almacenadas en la base de datos PostgreSQL deben protegerse mediante cifrado simétrico robusto (AES-256) o algoritmos de derivación de claves con salting para las funciones de búsqueda, acatando las regulaciones de protección de datos personales.

_(Módulo: Java / HU-2.1)_

**RNF-27 (Limitación de Tasa de Consultas - Rate Limiting):**

El servicio de inferencia conversacional debe implementar control de tasa (_rate limiting_) restringiendo a un máximo de 10 peticiones por minuto por cliente identificado o IP, respondiendo con `HTTP 429 Too Many Requests` para proteger la capacidad de cómputo de los modelos.

_(Módulo: Python / HU-1.8, HU-3.9)_

**RNF-28 (Cabeceras de Seguridad Web):**

El frontend y los puntos de entrada HTTP deben emitir cabeceras de seguridad estrictas: _Content-Security-Policy_ (CSP), _X-Frame-Options: DENY_, y _X-Content-Type-Options: nosniff_, mitigando vulnerabilidades de tipo XSS y Clickjacking.

_(Módulo: Frontend / HU-3.1)_

---

## Gobernanza de Inteligencia Artificial e Integridad Cuantitativa (MLOps)

**RNF-29 (Trazabilidad y Versionado de Modelos):**

Cada registro de inferencia consolidado en MongoDB debe registrar el identificador de versión específico o commit hash de los modelos MASTER y Galformer utilizados, garantizando la trazabilidad algorítmica ante auditorías.

_(Módulo: Python / HU-1.3, HU-1.4, HU-1.7)_

**RNF-30 (Actualización de Modelos sin Interrupción de Servicio):**

El despliegue o refresco de pesos y artefactos de Machine Learning en FastAPI debe realizarse en caliente (_zero-downtime_) o vía despliegues progresivos, sin desconectar las sesiones WebSocket ni detener la ingesta de datos.

_(Módulo: Python / HU-1.3, HU-1.4)_

**RNF-31 (Detección de Deriva de Datos - Data Drift):**

El pipeline analítico debe calcular periódicamente métricas estadísticas sobre los factores de entrada (Alpha Factors y retornos) para alertar a los administradores cuando las distribuciones de mercado diverjan significativamente de las ventanas de entrenamiento.

_(Módulo: Python / HU-1.2, HU-1.5)_

**RNF-32 (Aislamiento de Tiempos de Inferencia):**

La ejecución computacional de las redes neuronales no debe interferir con la recepción de ticks; las rutinas pesadas de inferencia de MASTER y Galformer deben desacoplarse en workers o hilos dedicados para no penalizar el bucle de eventos principal.

_(Módulo: Python / HU-1.3, HU-1.4)_

---

## Usabilidad, Accesibilidad y Ergonomía (UX/UI)

**RNF-33 (Punto de Entrada Unificado sin Fricción):**

La barra de búsqueda conversacional debe actuar como la vía central de acceso al motor de recomendaciones, prescindiendo de menús jerárquicos o breadcrumbs complejos como ruta obligatoria.

_(Módulo: Frontend / HU-3.1)_

**RNF-34 (Ocultamiento Progresivo de Complejidad - Complexity Hiding):**

La vista de resultados debe privilegiar explicaciones cualitativas en lenguaje natural accesible, dejando métricas técnicas crudas (z-scores, covarianzas) confinadas a paneles desplegables opcionales ("¿Por qué?") o al Hub Educativo.

_(Módulo: Frontend / HU-3.2, HU-3.6)_

**RNF-35 (Persistencia de Contexto de Navegación):**

El panel lateral del Hub Educativo debe abrirse en modalidad overlay sin recargar la pantalla, resetear los filtros ni alterar el estado analítico de la recomendación en curso.

_(Módulo: Frontend / HU-3.7)_

**RNF-36 (Validación de Formularios en el Cliente):**

El campo de búsqueda debe interceptar y bloquear el envío de entradas vacías o compuestas exclusivamente por espacios en blanco en el frontend, sin despachar peticiones de red al servidor.

_(Módulo: Frontend / HU-3.1)_

**RNF-37 (Tratamiento Semántico de Errores en Interfaz):**

Frente a caídas del backend o respuestas demoradas, la interfaz debe sustituir las alertas crudas del sistema por mensajes orientativos claros, ofreciendo alternativas de reintento en lugar de pantallas de carga indefinida.

_(Módulo: Frontend / HU-3.9)_

**RNF-38 (Accesibilidad y Contraste Visual - WCAG 2.1 AA):**

Los componentes de la interfaz, badges de señalización (`BUY`, `SELL`, `HOLD`) y gráficos interactivos deben respetar una relación de contraste cromático mínima de 4.5:1, garantizando su legibilidad en condiciones de deficiencia visual o daltonismo.

_(Módulo: Frontend / HU-3.3, HU-3.5, HU-3.6)_

**RNF-39 (Diseño Adaptable y Compatibilidad Multi-Navegador):**

La interfaz de usuario debe ofrecer una experiencia operativa fluida en pantallas desde 375px hasta resoluciones 4K, con soporte garantizado en las versiones estables recientes de los motores Blink (Chrome, Edge), Gecko (Firefox) y WebKit (Safari).

_(Módulo: Frontend / HU-3.1, HU-3.5)_

---

## Operabilidad, Telemetría y DevOps

**RNF-40 (Despliegue Determinista con Orquestación Única):**

El conjunto de servicios (FastAPI, Micronaut, Redis, PostgreSQL, MongoDB) debe ser desplegable en entornos de desarrollo y producción mediante un único archivo `docker-compose.yml`, orquestando dependencias y puertos de forma automatizada.

_(Módulo: Infraestructura / HU-4.1)_

**RNF-41 (Verificación de Salud de Contenedores - Healthchecks):**

Los contenedores orquestados deben incluir rutinas de verificación de salud (`HEALTHCHECK`), condicionando el arranque de los servicios de aplicación al estado completamente operativo de sus respectivas bases de datos.

_(Módulo: Infraestructura / HU-4.1)_

**RNF-42 (Registro Estructurado de Eventos - Structured Logging):**

Todos los servicios deben emitir bitácoras en formato JSON estructurado, incluyendo marca temporal ISO-8601, severidad, hilo de ejecución, módulo y mensaje contextualizado ante descartes de datos, fallos o cambios de estado.

_(Módulo: Transversal / HU-1.1, HU-1.4, HU-1.6)_

**RNF-43 (Trazabilidad Distribuida - Correlation ID):**

El sistema debe propagar un identificador único de trazabilidad (`Correlation-ID`) a través de la secuencia completa: desde el tick entrante en Python, pasando por la publicación en Redis, hasta la notificación y registro en PostgreSQL por el microservicio Java.

_(Módulo: Transversal / HU-1.1, HU-1.6, HU-2.2, HU-4.2)_

**RNF-44 (Exposición de Métricas de Rendimiento):**

Los microservicios deben exponer endpoints bajo `/metrics` compatibles con Prometheus, publicando la latencia del bucle de eventos, la profundidad de colas en memoria y las tasas de acierto del clasificador.

_(Módulo: Transversal / HU-4.1)_

**RNF-45 (Objetivos de Respaldo y Recuperación - RPO y RTO):**

Las bases de datos operativas deben contar con políticas de respaldo continuo que aseguren un Objetivo de Punto de Recuperación (RPO) menor a 1 hora y un Objetivo de Tiempo de Recuperación (RTO) inferior a 30 minutos frente a contingencias mayores de infraestructura.

_(Módulo: Infraestructura / HU-4.1, HU-4.2)_

---

## Trazabilidad Resumida de Requerimientos No Funcionales

| Categoría de Calidad                           | Rango RNF       | Componentes y Módulos Afectados                                                       |
| ---------------------------------------------- | --------------- | ------------------------------------------------------------------------------------- |
| **Rendimiento, Eficiencia y Capacidad**        | RNF-01 a RNF-06 | Ingesta Python, Pipeline MASTER/Galformer, Listener Java, MongoDB, Frontend           |
| **Confiabilidad y Resiliencia (Backpressure)** | RNF-07 a RNF-12 | WebSocket Streaming, Colas Asíncronas, Broker Redis, MongoDB Append-Only              |
| **Arquitectura, Mantenibilidad y Código**      | RNF-13 a RNF-18 | Dominio Java Hexagonal, Testing en Memoria, API RESTful, Chart.js, HikariCP           |
| **Reglas de Negocio, Ética y Riesgo Legal**    | RNF-19 a RNF-22 | Redacción Probabilística, Descargos Estadísticos, Prohibición de Mocks, Normalización |
| **Seguridad, Privacidad y Cumplimiento**       | RNF-23 a RNF-28 | UUID v4, Sanitización NLP, TLS 1.3, Cifrado de Emails, Rate Limiting, Cabeceras HTTP  |
| **Gobernanza de IA y MLOps**                   | RNF-29 a RNF-32 | Trazabilidad de Pesos, Zero-Downtime, Data Drift, Concurrencia de Inferencia          |
| **Usabilidad, Ergonomía y Accesibilidad**      | RNF-33 a RNF-39 | Input Guiado, Complexity Hiding, Hub Educativo, WCAG 2.1 AA, Diseño Responsive        |
| **Operabilidad, Telemetría y DevOps**          | RNF-40 a RNF-45 | Docker Compose, Healthchecks, Logging JSON, Trazabilidad Distribuida, Prometheus      |

_Total de Requerimientos No Funcionales: 45_

---

# 3. Consolidado General del Sistema

| Dimensión de Requerimientos               | Identificadores  | Cantidad Total |
| ----------------------------------------- | ---------------- | -------------- |
| **Requerimientos Funcionales (RF)**       | RF-01 al RF-49   | 49             |
| **Requerimientos No Funcionales (RNF)**   | RNF-01 al RNF-45 | 45             |
| **Total de Requerimientos Especificados** | **RF + RNF**     | **94**         |
