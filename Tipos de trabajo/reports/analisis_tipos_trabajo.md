# Análisis de Uso por "Tipo de Trabajo"

A partir de la revisión del archivo `resumen_trabajos.xlsx`, se ha realizado un análisis de los registros contenidos en las columnas "Causa visita", "Resolución visita" y "Observaciones" para determinar el perfil de uso de cada categoría de trabajo ("Tipo de trabajo").

A continuación se detallan los hallazgos para cada código identificado:

## 1. Tipo de Trabajo: C
**Definición de Uso:**  
Este código parece estar asociado a **Coordinación, Capacitación y Labores Administrativas**. Los registros indican actividades que no son necesariamente de intervención técnica directa en equipos (reparación/instalación), sino de gestión del conocimiento, reportes y logística.

*   **Actividades Principales:**
    *   Capacitación a operadores y personal administrativo.
    *   Elaboración y avance de informes técnicos y administrativos.
    *   Coordinación de entregas de equipos (e.g., motobombas) y gestión de usuarios.
    *   Soporte administrativo en terreno.

## 2. Tipo de Trabajo: G
**Definición de Uso:**  
Este tipo de trabajo tiene un volumen bajo de registros y parece centrarse en **Gestión de Hardware en Sala de Control** o Infraestructura General. Se observa un enfoque específico en monitores, pantallas y equipamiento de visualización.

*   **Actividades Principales:**
    *   Instalación y configuración de monitores y pantallas en salas de control.
    *   Retiro de equipos de visualización por falla.
    *   Entrega de equipos (caudalímetros) para gestión de terceros.

## 3. Tipo de Trabajo: I
**Definición de Uso:**  
Corresponde claramente a **Instalación e Integración**. Es uno de los códigos más utilizados y se centra en la puesta en marcha de nuevos puntos de monitoreo, sensores y sistemas de telemetría.

*   **Actividades Principales:**
    *   Instalación, conexión y configuración de telemetría y sensores (sondas multiparamétricas, niveles, etc.).
    *   Integración de soluciones (e.g., Flowcell, equipos Sutron, UC300).
    *   Configuración de variables en plataformas.
    *   Verificación inicial de funcionamiento y validación de datos en terreno.

## 4. Tipo de Trabajo: LT
**Definición de Uso:**  
Se identifica como **Levantamiento Técnico o de Terreno**. Su propósito es el diagnóstico, inspección y recolección de información previa a una intervención mayor o para documentar el estado actual de las instalaciones.

*   **Actividades Principales:**
    *   Levantamiento de información en terreno para futuros trabajos.
    *   Registro e inventario de instrumentación existente.
    *   Revisión diagnóstica de cables y componentes (e.g., sondas).
    *   Verificación de instalaciones para validar estándares (e.g., arranques, cuellos de cisne).

## 5. Tipo de Trabajo: MC
**Definición de Uso:**  
Corresponde a **Mantenimiento Correctivo**. Se utiliza cuando se asiste a resolver fallas, averías o realizar cambios de componentes dañados para restaurar la operatividad.

*   **Actividades Principales:**
    *   Reparación y reemplazo de tableros, sensores y cableado dañado.
    *   Solución de problemas de comunicación o energía.
    *   Re-configuración de equipos tras fallas o bloqueos.
    *   Canalización y arreglo de infraestructura en mal estado.

## 6. Tipo de Trabajo: MP
**Definición de Uso:**  
Se define como **Mantenimiento Preventivo**. A diferencia del MC, este trabajo es planificado y busca mantener la operatividad mediante limpieza, calibración y revisiones periódicas.

*   **Actividades Principales:**
    *   Limpieza de sensores, paneles solares y tableros.
    *   Cambio de sondas para rotación y calibración (gestión de certificados).
    *   Contrastación de mediciones y validación de datos.
    *   Revisión general de conexionado y programas de PLC.

## 7. Tipo de Trabajo: ST
**Definición de Uso:**  
Este código, **Soporte Técnico** o **Servicios de Terreno**, actúa como una categoría "comodín" o generalista con el mayor volumen de registros. Aunque incluye muchas actividades de *Mantenimiento Preventivo*, parece abarcar un espectro más amplio de solicitudes, incluyendo soporte ad-hoc, configuraciones específicas y requerimientos directos del cliente.

*   **Actividades Principales:**
    *   Mantenimiento preventivo (se traslapa significativamente con MP).
    *   Configuraciones específicas de equipos y transmisión.
    *   Atención a solicitudes puntuales (e.g., toma de fotografías, aumento de caudal).
    *   Soporte general e inspecciones visuales.
    *   Reseteo de equipos y recuperación de datos (tarjetas SD).

---
**Observación General:**
Existe una notable intersección entre **ST** y **MP**, ya que muchos registros en ST se describen explícitamente como "Mantenimiento preventivo". Sería recomendable evaluar si se deben unificar criterios para que todo mantenimiento preventivo quede bajo **MP**, dejando **ST** exclusivamente para soporte a demanda o incidencias no clasificables como correctivas puras.
