# Definición de Categorías y Casos de Uso

Este documento formaliza las definiciones de cada "Tipo de Trabajo" tras la reestructuración, proporcionando ejemplos concretos extraídos de los registros históricos para ilustrar su correcta aplicación.

---

## 1. MP - Mantenimiento Preventivo

**Definición:** Actividades planificadas y rutinarias destinadas a conservar la operatividad de los equipos y extender su vida útil. Incluye limpieza, inspección visual, reapriete de conexiones y contrastación de medidas.

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 305 | Leonardo Gonzalez | PI 17, PI 18, PI 19, PI 20 | Se realiza inspección visual y mantenimiento rutinario de tableros y planta solar. |
| 302 | Leonardo Gonzalez | PM-26 Nodo | Actividad explícita de limpieza de panel y reapriete de cables (conservación). |
| 302 | Leonardo Gonzalez | PM-6 Nodo 158 | Mantenimiento preventivo estándar: limpieza y revisión de voltaje. |
| 302 | Leonardo Gonzalez | P3a p3b y gateway ao1 | Limpieza y reapriete para asegurar continuidad operativa. |
| 300 | Elías Sanchez | R2700 Caudalimetro B | Verificación rutinaria de lecturas y cambio de tarjeta SD (gestión de datos preventiva). |
| 300 | Elías Sanchez | R3050 Gateway | Chequeo de funcionamiento y respaldo de datos preventivo. |
| 296 | Leonardo Gonzalez | PM-30 Nodo | Limpieza de panel solar y mediciones de voltaje para prevenir fallas de energía. |
| 296 | Leonardo Gonzalez | PM-28C Nodo | Mantenimiento estándar de energización y limpieza. |
| 296 | Leonardo Gonzalez | PM-1 Nodo B17 | Actividad periódica de conservación de infraestructura. |
| 296 | Leonardo Gonzalez | PM-07 Gate

---

## 2. MC - Mantenimiento Correctivo

**Definición:** Intervenciones reactivas destinadas a resolver fallas, averías o anomalías reportadas. Su objetivo es restaurar el funcionamiento normal tras un evento no deseado.

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 299 | Elías Sanchez | R2700 Caudalimetro B | Resolución de falla en el guardado de datos (el equipo no registraba). |
| 299 | Elías Sanchez | R3050 Gateway | Retiro de equipo por falla (inversor) para evaluación en laboratorio. |
| 292 | Leonardo Gonzalez | Sector -300 Gateway | Inspección de urgencia por reporte de rebalse (anomalía crítica). |
| 292 | Leonardo Gonzalez | Lora Piscina 3800 | Revisión de válvulas y caudal por solicitud ante comportamiento anómalo. |
| 292 | Leonardo Gonzalez | PEM 4, PEM 6... | Detección de vandalismo (daño físico) y revisión de estado. |
| 292 | Leonardo Gonzalez | Pozo N° 3A (P3A) | Verificación de sensores ante dudas en la medición. |
| 288 | Leonardo Gonzalez | Pozo Los Litres N° 01 | Revisión específica de sensor de nivel por inconsistencia o duda operativa. |
| 288 | Leonardo Gonzalez | Pozo Los Litres N° 02 | Diagnóstico de funcionamiento de sensor de nivel. |
| 288 | Leonardo Gonzalez | Pozo Los Litres N° 03 | Validación de medidas en terreno para descartar falla de sensor. |
| 288 | Leonardo Gonzalez | Pozo Los Litres N° 04 | Revisión correctiva de lectura de nivel. |

---

## 3. I - Instalación e Integración

**Definición:** Montaje, conexión y puesta en marcha de nuevos equipos o puntos de monitoreo. Incluye la configuración inicial necesaria para dejar el activo operativo.

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 304 | Camilo Sandoval | Pozo PME-09C | Instalación física de nueva sonda multiparamétrica e inventario inicial. |
| 293 | Juan José López | Pozo P3G | Cambio e instalación de sonda nueva por renovación tecnológica/falla de la anterior. |
| 293 | Juan José López | Pozo Dren MP Nodo | Habilitación completa: instalación de Sutron, cableado e integración de variables. |
| 293 | Juan José López | Pozo Dren MP Nodo | Configuración inicial de variables (pH, turbidez) como parte de la puesta en marcha. |
| 293 | Juan José López | Pozo P6 | Reemplazo e instalación de sonda para restaurar/mejorar medición. |
| 293 | Juan José López | Pozo Dren MO Gateway | Instalación de equipamiento de telemetría y sensores desde cero o renovación. |
| 291 | Juan José López | Pozo PMO-15C | Trabajo de conexión y configuración para integración de nuevo punto. |
| 291 | Juan José López | Pozo PP-31C | Intento de integración de punto (pendiente por falla de componente nuevo). |
| 290 | Cristopher Iglesias | R2700 Gateway | Trabajos de mejoramiento y verificación de instalación de UPS/Energía. |
| 202 | Juan José López | Bodega ASAP | Entrega de materiales para implementación de nuevos pozos (fase logística de instalación). |

---

## 4. CF - Configuración y Ajustes

**Definición:** Intervenciones lógicas en equipos ya operativos. Se centra en modificaciones de software, firmware, parámetros de lectura o transmisión, sin implicar obra física mayor.

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 299 | Elías Sanchez | R3050 Caudalimetro C | Ajuste de intervalo de transmisión (30 min) en equipo existente. |
| 278 | Elías Sanchez | Descarga el gallo mina UG | Configuración de transmisor Teledyne y comunicación Modbus (Software/Lógica). |
| 278 | Elías Sanchez | PI17 | Revisión y ajuste de programa de PLC por traba de válvula. |
| 267 | Cristopher Iglesias | R3050 Gateway | Configuración de parámetros de inversor y corrección lógica de circuito. |
| 266 | Elías Sanchez | Pozo Los Litres N° 01 | Modificación de rutina PLC para agregar variable "Volumen Acumulado". |
| 266 | Elías Sanchez | Pozo Los Litres N° 02 | Replica de configuración de rutina PLC en otro pozo. |
| 266 | Elías Sanchez | PM-2 Nodo B18 | Rescate (backup) de configuraciones de equipo UC300. |
| 266 | Elías Sanchez | Estero El Gallo | Configuración integral de sonda y rutinas de lectura en PLC. |
| 214 | David Loncopan | PSR Danone (Chillán) | Revisión y ajuste de comunicación Modbus RTU (Protocolos de comunicación). |
| 295 | Diego Marchant | Piscina UG | Configuración de equipo ISCO y lectura de variables Modbus. |

---

## 5. SO - Solicitud Operativa

**Definición:** Tareas realizadas a petición explícita del cliente que no corresponden a mantenimiento ni fallas, sino a necesidades operativas, logísticas o de asistencia.

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 302 | Leonardo Gonzalez | Piscina 4000 | Solicitud específica de "Toma de fotografías". |
| 302 | Leonardo Gonzalez | PI7 Nodo B7 | Ejecución de maniobra operativa: "Aumento de caudal". |
| 262 | Elías Sanchez | Estero El Gallo | Levantamiento Batimétrico para ingreso de datos a software (Tarea auxiliar). |
| 236 | Cristopher Iglesias | R2700 Gateway | Apoyo en bloqueo eléctrico para terceros o tareas generales. |
| 205 | Diego Marchant | Cachimba Relevadoras | Entrega de motobomba y gestión de usuarios a pedido del cliente. |
| 202 | Juan José López | Bodega ASAP | Entrega de materiales a terceros (Gestión logística). |
| 283 | Diego Marchant | Arranque BH TRET | Ronda de inspección y pruebas de presión a solicitud del cliente. |
| 207 | Juan José López | Varios | Entrega de llaves y reconocimiento de recintos con empresa externa (ASAP). |

---

## 6. LT - Levantamiento Técnico

**Definición:** Visitas de diagnóstico, inspección visual o recolección de información para planificar trabajos futuros. No implica intervención correctiva inmediata.

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 291 | Juan José López | Pozo P6 | Diagnóstico de situación: se identifica necesidad de cambiar sonda HL4. |
| 281 | Juan José López | Pozo PP-31C | Diagnóstico de falla en componente DDR30G-5 (se deja pendiente para cambio). |
| 257 | Juan José López | Pozo PP-29 | Verificación de estado de instalación (pendiente panel solar). |
| 257 | Juan José López | Pozo O4B | Inspección de estándares de instalación (cuello de cisne mal ubicado). |
| 234 | Leonardo Gonzalez | Reforestacion | Acompañamiento para levantamiento técnico en cerro. |
| 224 | Ángel Zamora | Biodiversa Chimbarongo | Ronda y levantamiento de puntos con cliente. |
| 216 | Ángel Zamora | Biodiversa Chimbarongo | Levantamiento de puntos adicionales e informe de hallazgos. |
| 207 | Juan José López | PME-10... | Recorrido de reconocimiento de instalaciones. |
| 198 | Andrés Valenzuela | Línea Bomba 6 | Verificación de punto de instalación y toma de medidas de flanges. |
| 283 | Diego Marchant | Arranque BH TRET | Inspección visual de nuevos medidores de presión. |

---

## 7. C - Coordinación y Capacitación

**Definición:** Actividades de gestión del conocimiento, entrenamiento a usuarios y labores administrativas de reporte.

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 248 | Juan José López | PP-31 | Elaboración de informe de avance (Trabajo de gabinete). |
| 247 | Juan José López | PP-31 | Trabajo administrativo: redacción de informes. |
| 205 | Diego Marchant | Cachimba Relevadoras | Coordinación de usuarios y entrega de equipos. |
| 171 | David Loncopan | Pozo Los Almendros | Capacitación a operadores en uso de plataforma. |
| 169 | Juan José López | Pbm4 y p6 | Gestión de solución temporal (Flowcell). |
| 160 | David Loncopan | Recinto Planta Principal | Capacitación formal a comité SSR. |
| 159 | David Loncopan | Recinto Pozo | Capacitación de plataforma EtWe. |
| 167 | Juan José López | PBM4 y p6 | Gestión de solución flowcell. |
| 162 | Juan José López | PBM4 y P6 | Gestión de compras y actualización de carta Gantt. |
| 161 | Juan José López | P6 y PBM4 | Levantamiento y gestión de solución a corto plazo. |

---

## 8. G - Gestión de Infraestructura

**Definición:** Categoría específica para la administración, instalación y mantenimiento de hardware en salas de control (monitores, pantallas, periféricos).

| OT | Técnico | Asset | Porqué entra dentro de la clasificación |
| :--- | :--- | :--- | :--- |
| 284 | Felipe Riquelme | Sala de control | Instalación y configuración de monitores en sala. |
| 206 | David Loncopan | Sala de control GNL | Retiro de pantallas por falla y gestión de backup. |
| 93 | Elías Sanchez | PEM-01 | Entrega de equipo (caudalímetro) para gestión de terceros. |
