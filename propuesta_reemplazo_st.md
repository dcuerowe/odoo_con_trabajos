# Propuesta para Reemplazo de la Categoría ST (Servicio Técnico)

El análisis de los 140 registros clasificados como **ST** revela que esta categoría funciona actualmente como un "contenedor general" que abarca múltiples tipos de trabajos. 

Para eliminar **ST**, se propone redistribuir sus registros en las categorías existentes y crear dos nuevas categorías específicas para capturar los casos que no calzan en las definiciones actuales.

## 1. Redistribución a Categorías Existentes

Gran parte de los trabajos **ST** corresponden claramente a categorías ya definidas:

*   **MP - Mantenimiento Preventivo**
    *   **Criterio:** Registros que mencionan explícitamente "Mantenimiento preventivo", "Limpieza", "Contrastación" o "Calibración" programada.
    *   **Impacto:** Aproximadamente el **35-40%** de los tickets ST deberían migrar a MP.
    *   *Ejemplo ST actual:* "Mantenimiento preventivo y contrastacion" -> **MP**

*   **MC - Mantenimiento Correctivo**
    *   **Criterio:** Registros relacionados con "Fallas", "Fugas", "Reparaciones", "Cambio de componentes dañados" o "Restauración de servicio".
    *   **Impacto:** Casos de "Fuga en flange", "Falla de bomba", "Cambio de transmisor por falla".
    *   *Ejemplo ST actual:* "Se observa fuga en flange... reconexión" -> **MC**

*   **I - Instalación e Integración**
    *   **Criterio:** Trabajos de "Montaje", "Instalación de nuevos equipos", "Canalización", "Integración de señales" o "Configuración inicial".
    *   **Impacto:** Muchos tickets ST describen instalaciones nuevas o mejoras.
    *   *Ejemplo ST actual:* "Montaje del sensor RQ30... canalización" -> **I**

*   **LT - Levantamiento Técnico**
    *   **Criterio:** Visitas de inspección visual, revisión de factibilidad o toma de datos sin intervención mayor.
    *   *Ejemplo ST actual:* "Revisión visual del punto y revisión en plataforma" -> **LT**

## 2. Nuevas Categorías Propuestas

Para los casos que no son mantenimientos puros ni instalaciones, se proponen estas nuevas definiciones:

### **SO - Soporte Operacional (Nuevo)**
*   **Definición:** Intervenciones solicitadas por el cliente para modificar el estado operativo de un sistema que **no presenta falla**, o para asistir en operaciones de terceros.
*   **Casos de uso:**
    *   Ajustes de parámetros a pedido (cambio de setpoints).
    *   Maniobras operativas (cierre/apertura de válvulas manuales).
    *   Apoyo técnico a otras empresas en terreno.
    *   Capacitaciones "in situ" no planificadas.
*   *Ejemplos de ST que irían aquí:* 
    *   "Se cierra válvula de piscina UG hacia piscina 3800 por solicitud de cliente."
    *   "Ajuste manual de transmisor de pulsos."
    *   "Apoyo a empresa MIES para utilizar cachimba."

### **D - Diagnóstico (Nuevo)**
*   **Definición:** Visitas enfocadas exclusivamente en identificar la causa raíz de un problema complejo cuando la solución no se implementa en el momento (requiere repuestos o planificación).
*   **Casos de uso:**
    *   Investigación de fallas de comunicación intermitentes.
    *   Evaluación de equipos dañados para cotizar reemplazo.
*   *Ejemplos de ST que irían aquí:*
    *   "Se realiza revisión... se mejora señal pero no se logra transmitir... pendiente."
    *   "Diagnóstico efectuado el día anterior."

## Resumen de la Estrategia

| Categoría Actual | Acción | Nueva Categoría Destino |
| :--- | :--- | :--- |
| **ST** (Preventivos) | **Reclasificar** | **MP** |
| **ST** (Correctivos/Fallas) | **Reclasificar** | **MC** |
| **ST** (Instalaciones) | **Reclasificar** | **I** |
| **ST** (Inspecciones) | **Reclasificar** | **LT** |
| **ST** (Solicitudes/Ajustes) | **Mover a Nueva** | **SO** (Soporte Operacional) |
| **ST** (Solo Diagnóstico) | **Mover a Nueva** | **D** (Diagnóstico) |

Esta estructura elimina la ambigüedad de "Servicio Técnico" y permite medir con precisión cuánto esfuerzo se dedica a fallas reales (MC) vs. solicitudes del cliente (SO) vs. mantenimiento programado (MP).

## 3. Tratamiento de Configuraciones y Reinicios

Para actividades específicas como **configuraciones** y **reinicios**, la clasificación depende del *contexto* y el *objetivo* de la acción:

### **Configuraciones**
*   **I - Instalación:** Si es la configuración inicial de un equipo nuevo o recién montado.
    *   *Ejemplo:* "Configuración de parámetros iniciales en sensor nuevo."
*   **SO - Soporte Operacional:** Si es un ajuste solicitado por el cliente para cambiar la operación (ej. cambiar setpoints, intervalos de lectura) en un equipo que funciona bien.
    *   *Ejemplo:* "Cambio de intervalo de envío de datos a solicitud del cliente."
*   **MC - Mantenimiento Correctivo:** Si se re-configura un equipo que perdió su programación o se ajusta para corregir una lectura errónea/falla.
    *   *Ejemplo:* "Re-configuración de escala de sensor por lecturas incoherentes."

### **Reinicios (Reset)**
*   **MC - Mantenimiento Correctivo:** Si el reinicio se realiza para "despegar" un equipo bloqueado o restablecer un servicio caído. Se considera una reparación menor.
    *   *Ejemplo:* "Reinicio de router por pérdida de comunicación."
*   **D - Diagnóstico:** Si se reinicia como prueba para ver si el problema persiste, sin ser la solución definitiva.
    *   *Ejemplo:* "Se reinicia equipo para descartar falla de software, problema persiste."

