# Propuesta Integral de Reestructuración de Categorías de Trabajo

Este documento consolida las propuestas para la eliminación de la categoría **ST (Soporte Técnico)** y la creación de nuevas categorías específicas, con el objetivo de mejorar la calidad de la información registrada y obtener métricas más precisas sobre las operaciones en terreno.

## 1. Diagnóstico: El Problema de la Categoría "ST"

El análisis de los registros históricos confirma que la categoría **ST** actúa como un contenedor genérico ("comodín") que diluye la información valiosa.

* **33%** de los registros son en realidad **Mantenimiento Preventivo**.
* **20%** son **Mantenimiento Correctivo**.
* **20%** son **Instalaciones**.
* El resto se divide entre configuraciones lógicas y solicitudes operativas del cliente.

**Objetivo:** Eliminar la categoría **ST** y redistribuir sus registros en categorías que describan *qué se hizo* y no *quién lo pidió*.

---

## 2. Nueva Estructura de Categorías

Para absorber la carga de trabajo de ST y capturar mejor la realidad operativa, se propone el siguiente esquema de categorías:

### A. Categorías Existentes (Reforzadas)

| Código | Categoría | Definición Reforzada | Criterio de Inclusión |
| :--- | :--- | :--- | :--- |
| **MP** | **Mantenimiento Preventivo** | Actividades planificadas para conservar la operatividad. | Limpieza, calibración física, contrastación, revisión rutinaria. |
| **MC** | **Mantenimiento Correctivo** | Resolución de fallas y averías para restaurar el servicio. | Reparaciones, cambio de componentes dañados, reinicio por "cuelgue". |
| **I** | **Instalación e Integración** | Montaje y puesta en marcha de *nuevos* equipos. | Instalación física, conexionado, y la configuración *inicial* asociada. |
| **LT** | **Levantamiento Técnico** | Diagnóstico y recolección de información sin intervención mayor. | Inspecciones visuales, inventarios, cotizaciones. |

### B. Nuevas Categorías Propuestas

Se introducen dos nuevas categorías para cubrir vacíos específicos que antes caían en el "saco roto" de ST:

#### 1. SO - Solicitud Operativa

* **Definición:** Trabajos realizados a petición explícita del cliente que implican operar el sistema o realizar tareas auxiliares que no son fallas ni mantenimientos estándar.
* **Ejemplos:**
  * "Aumento o disminución de caudal" (Operación).
  * "Toma de fotografías de estado de piscina".
  * "Apoyo/Acompañamiento a empresas externas".
  * "Entrega de llaves o materiales".

#### 2. CF - Configuración y Ajustes

* **Definición:** Intervenciones técnicas enfocadas exclusivamente en el **software, firmware o parámetros lógicos** de equipos *ya instalados y operativos*. Diferencia el esfuerzo "intelectual/lógico" del esfuerzo "físico" de instalación o reparación.
* **Ejemplos:**
  * Modificación de factores K, offsets o setpoints.
  * Cambios en intervalos de transmisión/logueo.
  * Actualización de Firmware.
  * Integración de nuevas variables en dataloggers existentes.
* **Exclusión:** Si la configuración es parte de la instalación inicial, va en **I**.

---

## 3. Matriz de Migración (De ST a la Nueva Estructura)

A continuación, se detalla cómo deben reclasificarse los registros que históricamente se etiquetaban como **ST**:

| Registro Típico en "ST" | Nueva Categoría | Justificación |
| :--- | :---: | :--- |
| *"Mantenimiento preventivo y limpieza"* | **MP** | Actividad de conservación planificada. |
| *"Revisión por falla de comunicación"* | **MC** | Resolución de una avería. |
| *"Cambio de cable cortado"* | **MC** | Reparación física. |
| *"Instalación de soporte y sensor"* | **I** | Montaje de nuevo equipamiento. |
| *"Configuración de parámetros (Factor K)"* | **CF** | Ajuste lógico en equipo existente (No es falla ni obra nueva). |
| *"Actualización de firmware"* | **CF** | Mejora de software. |
| *"Aumento de caudal a solicitud"* | **SO** | Operación del sistema (No es mantenimiento). |
| *"Toma de fotografías"* | **SO** | Tarea auxiliar a pedido. |
| *"Levantamiento de información"* | **LT** | Diagnóstico sin intervención. |

---

## 4. Beneficios de la Reestructuración

1. **Claridad en Mantenimiento:** Se podrá distinguir con precisión cuánto esfuerzo se dedica a prevenir (**MP**) vs. corregir (**MC**).
2. **Visibilidad de Especialización:** La categoría **CF** permitirá medir la carga de trabajo de los especialistas en telemetría/software, separándola de la labor de montaje físico (**I**).
3. **Atención al Cliente:** La categoría **SO** visibilizará cuánto tiempo se invierte en "favores" o asistencia operativa al cliente, lo cual es clave para la gestión comercial.
4. **Eliminación de Ambigüedad:** Al desaparecer **ST**, se fuerza una clasificación basada en la *naturaleza técnica* del trabajo.
