# Especificación Detallada de Casos de Uso e Historias de Usuario

## Plataforma Cuantitativa de Inversión Predictiva

**Propósito del documento:** Proporcionar la especificación funcional y técnica detallada para el modelado formal de casos de uso (UML 2.5), garantizando trazabilidad directa con los requerimientos funcionales (RF), no funcionales (RNF) y las historias de usuario (HU).

**Estructura de cada ficha:**

- **Identificador y Nombre:** Código normalizado y denominación de la meta del actor.
- **Trazabilidad:** Historia de usuario y requerimientos asociados.
- **Actor(es):** Iniciador primario o sistema externo secundario participante.
- **Disparador (Trigger):** Evento o acción concreta que inicia la ejecución.
- **Precondiciones:** Estado del sistema requerido previo a la ejecución.
- **Flujo principal:** Secuencia nominal de interacción ("camino feliz").
- **Flujos alternos / Excepciones:** Variantes y gestión de errores.
- **Postcondiciones:** Estado garantizado tras una ejecución exitosa.
- **Reglas de negocio y RNF asociados:** Restricciones normativas, legales o de diseño.
- **Puntos de extensión / Relaciones UML:** Conexiones formales (`<<include>>` / `<<extend>>`).

---

## UC-01 — Ingresar Intención de Inversión

- **Trazabilidad:** HU-3.1 | RF-01, RF-02, RF-03, RF-30, RF-31, RF-32, RF-33 | RNF-04, RNF-16, RNF-19, RNF-24, RNF-33, RNF-36
- **Actor(es):** Usuario Final (Primario).
- **Disparador:** El usuario redacta una consulta en lenguaje natural en la barra de búsqueda central y confirma el envío (Enter o clic en botón de búsqueda).
- **Precondiciones:**

1. La aplicación web se encuentra cargada en la vista principal (_home_).
2. El acceso es público/exploratorio; no requiere sesión autenticada obligatoria para la consulta.

- **Flujo principal:**

1. El usuario visualiza la barra de búsqueda conversacional en el centro de la interfaz.
2. El usuario ingresa un prompt en texto libre (ejemplos: _"Invertir 20000"_, _"Asignar 5000 a tecnología"_, _"Analizar Apple"_).
3. El usuario envía la consulta.
4. El frontend valida que el texto no esté vacío y despacha la petición al motor de clasificación.
5. El sistema clasifica el prompt dentro de una de tres categorías canónicas:

- `INTENT_MACRO`: Presupuesto sin sector especificado (distribución diversificada).
- `INTENT_SECTORIAL`: Presupuesto acoplado a una industria específica.
- `INTENT_ACTIVO`: Identificador o nombre de un activo individual.

6. El sistema redirige la interfaz a la vista analítica correspondiente al tipo de intención identificada.

- **Flujos alternos / Excepciones:**
- **3a. Prompt no interpretable:** Si la entrada no contiene entidades financieras reconocibles, el sistema no cambia de vista; despliega una alerta amigable solicitando al usuario que reformule o detalle su consulta.
- **3b. Campo vacío o espacios en blanco:** La interfaz intercepta el evento en el cliente, bloqueando la petición HTTP y mostrando una advertencia contextual.

- **Postcondiciones:** El usuario es posicionado en la vista analítica adecuada con el contexto de su búsqueda listo para ser procesado.
- **Reglas de negocio:**
- La barra conversacional es el canal primario de acceso a las recomendaciones; no existe navegación jerárquica obligatoria por menús para este fin.

- **Relaciones UML:**
- `<<include>>` **UC-02 (Ver Recomendación de Inversión):** Toda intención clasificada válidamente desencadena obligatoriamente la generación y renderizado de la recomendación.

---

## UC-02 — Ver Recomendación de Inversión

- **Trazabilidad:** HU-3.9, HU-1.8 | RF-04, RF-17, RF-18, RF-19, RF-20, RF-44, RF-45 | RNF-02, RNF-03, RNF-11, RNF-15, RNF-20, RNF-21, RNF-37
- **Actor(es):** Usuario Final (Primario), API de Predicción / Backend (Secundario / `<<system>>`).
- **Disparador:** Invocación automática tras la clasificación exitosa en UC-01.
- **Precondiciones:** Existencia de un payload de intención clasificado (`INTENT_MACRO`, `INTENT_SECTORIAL` o `INTENT_ACTIVO`).
- **Flujo principal:**

1. El cliente web despacha la solicitud estructurada hacia el endpoint `POST /api/v1/predict/intent`.
2. El backend procesa la petición a través del pipeline analítico (Qlib $\rightarrow$ MASTER $\rightarrow$ Galformer $\rightarrow$ Filtro de significancia estadística Z-test).
3. El backend responde con la estructura de recomendación (ponderaciones de capital, activos evaluados, z-score, p-value y métricas de soporte).
4. El frontend procesa la respuesta y renderiza los componentes de la vista analítica con los datos reales calculados.

- **Flujos alternos / Excepciones:**
- **2a. Timeout o fallo de red del backend:** La interfaz captura el error HTTP o corte de conexión y despliega un panel de degradación elegante con opción de reintento, evitando estados de carga infinita o exposición de trazas de error crudas.
- **2b. Datos insuficientes para el activo analizado:** Si el activo posee menos de 30 observaciones históricas o varianza nula, el sistema notifica claramente la indisponibilidad de masa crítica estadística para generar inferencias.

- **Postcondiciones:** El usuario visualiza la propuesta de inversión respaldada por cálculos en firme del pipeline cuantitativo.
- **Reglas de negocio:**
- Prohibición absoluta de datos simulados (_mocks_) o respuestas estáticas en entornos productivos.

- **Puntos de extensión declarados (Extension Points):**
- `Solicitud de fundamentación analítica`: Punto de anclaje para UC-03.
- `Recomendación macro o sectorial`: Punto de anclaje condicional para UC-05.
- `Ajuste manual de asignación`: Punto de anclaje para UC-06.
- `Inspección de activo individual`: Punto de anclaje para UC-07.

- **Relaciones UML:**
- Incluido por (`<<include>>`) **UC-01**.
- `<<include>>` **UC-04 (Visualizar Indicador de Confianza):** La confianza estadística acompaña siempre a cualquier recomendación renderizada.
- Extendido por (`<<extend>>`) **UC-03, UC-05, UC-06, UC-07**.
- Asociación de comunicación con el actor secundario **API de Predicción / Backend**.

---

## UC-03 — Consultar Explicación ("¿Por qué?")

- **Trazabilidad:** HU-3.2 | RF-06, RF-34, RF-35 | RNF-07, RNF-13, RNF-17, RNF-19, RNF-34
- **Actor(es):** Usuario Final.
- **Disparador:** El usuario acciona el control interactivo "¿Por qué?" situado en la tarjeta de recomendación.
- **Precondiciones:** UC-02 ejecutado con éxito; existe una recomendación activa en pantalla.
- **Flujo principal:**

1. El usuario hace clic sobre el botón o enlace "¿Por qué?".
2. El sistema despliega un panel contextual desplegable (_accordion_ o modal ligero).
3. El sistema expone la justificación cualitativa: tendencias intersectoriales detectadas y grado de consistencia estadística detrás de la señal.
4. El usuario consulta el razonamiento y colapsa el panel cuando lo considere pertinente.

- **Flujos alternos / Excepciones:** No presenta rutas de excepción operativas al tratarse de la presentación de metadatos analíticos ya cargados en memoria.
- **Postcondiciones:** El usuario comprende el fundamento técnico del algoritmo sin verse expuesto a formulaciones matemáticas densas.
- **Reglas de negocio:**
- El motor de generación de explicaciones tiene prohibido el empleo de verbos en futuro categórico (ej. _"subirá"_, _"obtendrás rentabilidad"_). Debe restringirse al uso de construcciones condicionales y probabilísticas.
- Se evita la exposición directa de jerga econométrica cruda sin contexto; los conceptos técnicos enlazan directamente a sus definiciones del glosario.

- **Relaciones UML:**
- `<<extend>>` **UC-02** (Punto de extensión: _Solicitud de fundamentación analítica_).

---

## UC-04 — Visualizar Indicador de Confianza

- **Trazabilidad:** HU-3.3 | RF-05, RF-09, RF-10, RF-36 | RNF-02, RNF-14, RNF-20, RNF-38
- **Actor(es):** Usuario Final.
- **Disparador:** Ejecución automática integrada al renderizado de UC-02 (no requiere invocación independiente del usuario).
- **Precondiciones:** La recomendación provista por el backend contiene el cálculo de significancia estadística ($p$-value derivado del test de hipótesis Z-test con $\alpha = 0.05$).
- **Flujo principal:**

1. Durante el montaje de la vista de recomendación, el sistema extrae el valor estadístico.
2. El sistema proyecta visualmente el indicador porcentual de consistencia.
3. De manera contigua e inseparable, el sistema muestra el texto legal aclaratorio de interpretación.

- **Flujos alternos / Excepciones:** No aplica; es un componente gráfico mandatorio de la interfaz analítica.
- **Postcondiciones:** La interfaz expone la métrica de consistencia junto con su delimitación legal de responsabilidad.
- **Reglas de negocio:**
- El texto aclaratorio debe especificar obligatoriamente que el porcentaje refleja la solidez de la evidencia estadística histórica del modelo y **nunca** una garantía o probabilidad de éxito financiero o retorno de capital.

- **Relaciones UML:**
- Incluido obligatoriamente (`<<include>>`) por **UC-02**.

---

## UC-05 — Visualizar Contexto Macroeconómico

- **Trazabilidad:** HU-3.4 | RF-07, RF-37 | RNF-13, RNF-17, RNF-19
- **Actor(es):** Usuario Final.
- **Disparador:** Renderizado condicional en pantalla al cumplirse la precondición de negocio en UC-02.
- **Precondiciones:** La recomendación generada corresponde a una categoría macroestructural (`INTENT_MACRO`) o de industria (`INTENT_SECTORIAL`).
- **Flujo principal:**

1. El sistema evalúa el tipo de recomendación activa.
2. El sistema incorpora en la vista un bloque dedicado al análisis macroeconómico sectorial.
3. Se describen tendencias globales del entorno de mercado, correlaciones entre industrias identificadas por MASTER y factores de riesgo sistémico.
4. El usuario asimila las variables del entorno macroeconómico que condicionan la propuesta.

- **Flujos alternos / Excepciones:**
- **2a. Contexto macro no disponible:** Si el pipeline no consolida información cualitativa suficiente para el sector consultado, el bloque se omite silenciosamente sin dejar contenedores vacíos ni alterar la gráfica de asignación.

- **Postcondiciones:** El usuario dispone de una visión contextualizada del ciclo económico que rodea su consulta.
- **Reglas de negocio:** Conservación de redacción bajo marcos probabilísticos y condicionales.
- **Relaciones UML:**
- `<<extend>>` **UC-02** (Punto de extensión: _Recomendación macro o sectorial_).

---

## UC-06 — Ajustar Distribución de Capital

- **Trazabilidad:** HU-3.5 | RF-08, RF-09, RF-38, RF-39 | RNF-09, RNF-12, RNF-16, RNF-22, RNF-38
- **Actor(es):** Usuario Final.
- **Disparador:** El usuario manipula los controles de ajuste porcentual o deslizadores del gráfico interactivo de asignación.
- **Precondiciones:** UC-02 ejecutado; la recomendación presenta una gráfica de distribución de activos/sectores construida mediante Chart.js.
- **Flujo principal:**

1. El usuario visualiza la torta o barras de distribución de capital propuesta.
2. El usuario altera interactivamente la ponderación de uno o más activos/sectores.
3. El sistema aplica validación de suma cerrada sobre las participaciones.
4. El frontend destruye la instancia gráfica previa del canvas y genera una nueva instancia renderizada con el escenario de capital rebalanceado.

- **Flujos alternos / Excepciones:**
- **3a. Ponderación acumulada inconsistente ($\neq 100\%$):** El sistema activa una rutina de normalización automática proporcional sobre el resto de las posiciones, o bien bloquea la confirmación del nuevo escenario resaltando el diferencial en color de advertencia.

- **Postcondiciones:** El usuario obtiene una proyección patrimonial adaptada a sus preferencias manuales sobre el gráfico.
- **Reglas de negocio:**
- La suma de las ponderaciones porcentuales de la cartera debe totalizar exactamente el 100%.
- La instancia de Chart.js debe ser destruida explícitamente en memoria antes de instanciar la nueva para evitar fugas de recursos en el navegador.

- **Relaciones UML:**
- `<<extend>>` **UC-02** (Punto de extensión: _Ajuste manual de asignación_).

---

## UC-07 — Visualizar Estrategias de Salida (Stop-loss / Take-profit)

- **Trazabilidad:** HU-3.6 | RF-10, RF-40 | RNF-13, RNF-17, RNF-34, RNF-38
- **Actor(es):** Usuario Final.
- **Disparador:** El usuario presiona el botón de detalle técnico o expande la fila de un activo individual dentro de la lista de recomendación.
- **Precondiciones:** UC-02 renderizado; la recomendación desglosa activos puntuales con niveles de precios objetivo y umbrales de mitigación calculados.
- **Flujo principal:**

1. El usuario selecciona la opción de ver detalle de un activo puntual.
2. El sistema despliega los niveles calculados de _Stop-loss_ (límite de pérdida sugerido) y _Take-profit_ (toma de ganancias sugerida).
3. El sistema muestra una descripción sintetizada y legible de la función de cada límite técnico.

- **Flujos alternos / Excepciones:** No presenta rutas de excepción; si el activo no cuenta con datos de soporte para calcular niveles, los campos se marcan como "No disponible temporalmente".
- **Postcondiciones:** El usuario conoce parámetros concretos de gestión de riesgo sobre la posición analizada.
- **Reglas de negocio:** Las explicaciones deben mantenerse accesibles para usuarios noveles bajo el principio de ocultamiento de complejidad (_complexity hiding_).
- **Relaciones UML:**
- `<<extend>>` **UC-02** (Punto de extensión: _Inspección de activo individual_).

---

## UC-08 — Consultar Hub Educativo

- **Trazabilidad:** HU-3.7 | RF-11, RF-41, RF-42 | RNF-06, RNF-07, RNF-17, RNF-18, RNF-34, RNF-35
- **Actor(es):** Usuario Final.
- **Disparador:** El usuario hace clic en el acceso directo del "Hub Educativo" de la barra de navegación, o pulsa sobre un concepto técnico resaltado en un texto explicativo (ej. _$p$-value_, _volatilidad_, _Galformer_).
- **Precondiciones:** Ninguna. Es un módulo transversal accesible en cualquier momento y estado de la sesión.
- **Flujo principal:**

1. El usuario invoca el glosario (por botón global o por enlace en término resaltado).
2. El sistema despliega un panel lateral deslizante (_drawer overlay_), posicionando el foco directamente en la definición del término seleccionado (o en el listado alfabético si fue apertura general).
3. El usuario lee el contenido pedagógico o busca conceptos adicionales mediante el filtro del panel.
4. El usuario cierra el panel lateral.

- **Flujos alternos / Excepciones:** No aplican flujos de error al tratarse de contenido estructurado estático.
- **Postcondiciones:** El usuario solventa dudas conceptuales sin alterar el estado operativo de la pantalla subyacente.
- **Reglas de negocio:** La invocación, navegación y cierre del Hub Educativo no deben recargar la página web, borrar datos en formularios ni reiniciar cálculos o visualizaciones en curso.
- **Relaciones UML:** Caso de uso autónomo/independiente. No mantiene relaciones de inclusión ni extensión con el flujo de recomendaciones.

---

## UC-09a — Registrarse en la Plataforma

- **Trazabilidad:** HU-2.1 | RF-12, RF-21 | RNF-21, RNF-23, RNF-26, RNF-32
- **Actor(es):** Usuario Final.
- **Disparador:** El usuario selecciona la opción "Registrarse" o "Crear Cuenta" desde la interfaz.
- **Precondiciones:** El usuario dispone de una dirección de correo electrónico válida y no registrada previamente.
- **Flujo principal:**

1. El sistema presenta el formulario de registro solicitando la dirección de correo electrónico.
2. El usuario introduce su correo y confirma el registro.
3. El sistema valida el formato del correo y verifica la unicidad de la cuenta.
4. El backend en Java genera un identificador criptográfico único (UUID versión 4).
5. El sistema almacena la nueva entidad de usuario en la base de datos PostgreSQL aplicando los estándares de protección y cifrado definidos.
6. El sistema confirma la creación exitosa de la cuenta y establece la sesión del usuario.

- **Flujos alternos / Excepciones:**
- **3a. Dirección de correo malformada:** El sistema detiene el flujo en el cliente y señala los requerimientos sintácticos del campo.
- **3b. Correo ya existente:** El backend retorna conflicto (`HTTP 409 Conflict`); la interfaz informa que el correo ya está en uso y sugiere iniciar sesión o recuperar acceso.

- **Postcondiciones:** Existe un nuevo registro de usuario formalmente persistido en el sistema con UUID asignado.
- **Relaciones UML:** Caso de uso independiente dentro del subsistema de gestión de cuentas.

---

## UC-09b — Configurar Alertas de Ticker

- **Trazabilidad:** HU-2.1, HU-2.2 | RF-13, RF-22, RF-24, RF-25 | RNF-04, RNF-10, RNF-17, RNF-41
- **Actor(es):** Usuario Final.
- **Disparador:** El usuario accede a la sección de preferencias de notificación de su perfil o pulsa "Crear alerta sobre este activo" en una recomendación.
- **Precondiciones:**

1. El usuario se encuentra autenticado en el sistema (cuenta creada en UC-09a).
2. El activo a monitorear existe en el universo de cobertura de la plataforma.

- **Flujo principal:**

1. El usuario selecciona el activo de interés ingresando el ticker correspondiente (`target_ticker`).
2. El usuario activa el selector de habilitación de notificaciones (`alerts_enabled = true`).
3. El usuario guarda la configuración.
4. El sistema actualiza y persiste la configuración del usuario en la base de datos relacional.
5. El microservicio Java incorpora de inmediato la suscripción a su memoria de evaluación para cotejo continuo contra las señales emitidas por el bus Redis (`market_signals`).

- **Flujos alternos / Excepciones:**
- **1a. Ticker inexistente o fuera de cobertura:** El sistema informa que el activo ingresado no forma parte del catálogo de streaming soportado.

- **Postcondiciones:** La suscripción del usuario queda activa para ser evaluada en tiempo de ejecución ante eventos analíticos del mercado.
- **Relaciones UML:** Caso de uso independiente dentro del subsistema de alertas (asume autenticación previa de UC-09a como precondición de negocio).

---

## UC-10 — Consultar Historial de Alertas

- **Trazabilidad:** HU-2.3 | RF-14, RF-26, RF-27, RF-48 | RNF-04, RNF-17, RNF-43
- **Actor(es):** Usuario Final.
- **Disparador:** El usuario accede al apartado "Historial de Alertas" dentro del menú de su perfil.
- **Precondiciones:** El usuario está autenticado en la plataforma.
- **Flujo principal:**

1. El usuario navega a la sección de alertas disparadas.
2. El frontend solicita el histórico al servicio en Java.
3. El sistema consulta los registros de la tabla `alert_history` asociados al identificador del usuario.
4. El sistema presenta la lista de señales recibidas ordenadas de manera descendente por fecha (`triggered_at`), exponiendo: ticker, precio de mercado al momento del cruce, tipo de señal (`BUY`/`SELL`) y estampa de tiempo.

- **Flujos alternos / Excepciones:**
- **3a. Usuario sin eventos generados:** El sistema despliega una vista limpia indicando el estado vacío (_empty state_: _"Aún no se han disparado alertas para tus tickers seguidos"_), sin emitir códigos ni estados de error.

- **Postcondiciones:** El usuario inspecciona la trazabilidad cronológica de las alertas emitidas a su cuenta.
- **Relaciones UML:** Caso de uso independiente dentro del subsistema de alertas.

---

# 3. Síntesis y Matrices para el Modelado UML

### Inventario de Actores

| Actor                           | Clasificación UML | Naturaleza                     | Responsabilidad en el Sistema                                                                                                                    |
| ------------------------------- | ----------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Usuario Final**               | Primario          | Humano                         | Dispara búsquedas en lenguaje natural, ajusta escenarios de inversión, consulta conceptos pedagógicos, gestiona su cuenta y parametriza alertas. |
| **API de Predicción / Backend** | Secundario        | Sistema Externo (`<<system>>`) | Servicio analítico que ejecuta los modelos cuantitativos (Qlib, MASTER, Galformer) y provee los datos estructurados a UC-02.                     |

---

### Matriz de Relaciones del Diagrama de Casos de Uso

| Caso Origen | Relación      | Caso Destino | Fundamento Metodológico y Criterio de Diseño                                                                                                |
| ----------- | ------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **UC-01**   | `<<include>>` | **UC-02**    | Toda intención clasificada válidamente desencadena obligatoriamente el renderizado de una recomendación de inversión.                       |
| **UC-02**   | `<<include>>` | **UC-04**    | Ninguna recomendación puede visualizarse sin exhibir su correspondiente indicador de confianza estadística ($p$-value).                     |
| **UC-03**   | `<<extend>>`  | **UC-02**    | La consulta de la explicación cualitativa ("¿Por qué?") es una decisión opcional del usuario sobre una recomendación ya renderizada.        |
| **UC-05**   | `<<extend>>`  | **UC-02**    | El bloque de contexto macroeconómico es una extensión condicional que sólo se manifiesta en recomendaciones de tipo macro o sectorial.      |
| **UC-06**   | `<<extend>>`  | **UC-02**    | El ajuste dinámico de capital es un comportamiento interactivo opcional que el usuario puede o no activar sobre el gráfico.                 |
| **UC-07**   | `<<extend>>`  | **UC-02**    | La visualización de estrategias de salida (_Stop-loss_ / _Take-profit_) depende de que el usuario decida inspeccionar un activo individual. |
| **UC-08**   | _Autónomo_    | N/A          | El Hub Educativo es transversal y está disponible en todo momento sin acoplamiento a los flujos de inferencia.                              |
| **UC-09a**  | _Autónomo_    | N/A          | Flujo independiente de autenticación y gestión de identidad de usuario (UUID).                                                              |
| **UC-09b**  | _Autónomo_    | N/A          | Flujo de parametrización de alertas (dependencia contextual de datos con UC-09a como precondición).                                         |
| **UC-10**   | _Autónomo_    | N/A          | Consulta de registros históricos de notificaciones almacenadas en PostgreSQL.                                                               |

---

### Trazabilidad Bidireccional: Casos de Uso vs. Requerimientos

| Caso de Uso | Historia de Usuario Origen | Requerimientos Funcionales (RF)    | Requerimientos No Funcionales (RNF)                    |
| ----------- | -------------------------- | ---------------------------------- | ------------------------------------------------------ |
| **UC-01**   | HU-3.1                     | RF-01, RF-02, RF-03, RF-30 a RF-33 | RNF-04, RNF-16, RNF-19, RNF-24, RNF-33, RNF-36         |
| **UC-02**   | HU-3.9, HU-1.8             | RF-04, RF-17 a RF-20, RF-44, RF-45 | RNF-02, RNF-03, RNF-11, RNF-15, RNF-20, RNF-21, RNF-37 |
| **UC-03**   | HU-3.2                     | RF-06, RF-34, RF-35                | RNF-07, RNF-13, RNF-17, RNF-19, RNF-34                 |
| **UC-04**   | HU-3.3                     | RF-05, RF-09, RF-10, RF-36         | RNF-02, RNF-14, RNF-20, RNF-38                         |
| **UC-05**   | HU-3.4                     | RF-07, RF-37                       | RNF-13, RNF-17, RNF-19                                 |
| **UC-06**   | HU-3.5                     | RF-08, RF-09, RF-38, RF-39         | RNF-09, RNF-12, RNF-16, RNF-22, RNF-38                 |
| **UC-07**   | HU-3.6                     | RF-10, RF-40                       | RNF-13, RNF-17, RNF-34, RNF-38                         |
| **UC-08**   | HU-3.7                     | RF-11, RF-41, RF-42                | RNF-06, RNF-07, RNF-17, RNF-18, RNF-34, RNF-35         |
| **UC-09a**  | HU-2.1                     | RF-12, RF-21                       | RNF-21, RNF-23, RNF-26, RNF-32                         |
| **UC-09b**  | HU-2.1, HU-2.2             | RF-13, RF-22, RF-24, RF-25         | RNF-04, RNF-10, RNF-17, RNF-41                         |
| **UC-10**   | HU-2.3                     | RF-14, RF-26, RF-27, RF-48         | RNF-04, RNF-17, RNF-43                                 |
