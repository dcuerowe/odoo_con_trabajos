# QA — Aseguramiento de calidad

Este directorio contiene la estrategia, el plan, los casos de prueba y los datos de prueba
del sistema de sincronización Connecteam → SharePoint.

## Índice

| Documento | Contenido |
| --- | --- |
| [01_estrategia_qa.md](01_estrategia_qa.md) | Enfoque, alcance, niveles de prueba y riesgos. |
| [02_plan_de_pruebas.md](02_plan_de_pruebas.md) | Plan por módulo, entorno y criterios de entrada/salida. |
| [03_casos_de_prueba.md](03_casos_de_prueba.md) | Casos de prueba detallados con pasos y resultados esperados. |
| [04_datos_de_prueba.md](04_datos_de_prueba.md) | Fixtures, JSON de ejemplo y construcción de DataFrames de prueba. |
| [05_checklist_release.md](05_checklist_release.md) | Lista de verificación previa a despliegue. |
| [06_resultados_ejecucion.md](06_resultados_ejecucion.md) | Resultados de la última ejecución de la suite automatizada. |
| [tests/](tests/) | Suite de pruebas automatizadas ejecutable con `pytest`. |

## Contexto

El proyecto no incluye una suite de tests ni un linter configurados. La validación
histórica se realiza ejecutando `main_practice.py` contra OT conocidas. Esta documentación
formaliza esa práctica y propone casos reproducibles, sin asumir infraestructura de
testing aún inexistente. Los ejemplos de código de prueba (basados en `pytest`) son una
referencia recomendada; su adopción requiere agregar `pytest` a las dependencias.

## Principios

- **Aislar de servicios externos**: las pruebas unitarias deben simular (mock) las llamadas
  a Connecteam y a Microsoft Graph. Ninguna prueba automatizada debe escribir en el
  `Terreno.xlsx` de producción.
- **Proteger la base de deduplicación**: las pruebas que tocan SQLite deben operar sobre una
  copia temporal de `form_entries.db`, nunca sobre el archivo versionado.
- **Cobertura por tipo de trabajo**: cada tipo (`MC`, `MP`, `I`, `R`, `E`, `CF`, `SO`, `LT`,
  `C`, `G`) y cada ruta de inspección debe tener al menos un caso.
