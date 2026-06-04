# Documentación General — Sincronización Connecteam → SharePoint

Este directorio contiene la documentación técnica del sistema de sincronización de
formularios de terreno. El sistema es un pipeline batch que extrae formularios
rellenados por técnicos de terreno desde Connecteam, los normaliza y los carga en un
libro Excel alojado en SharePoint que actúa como modelo de datos para dashboards.

## Índice

| Documento | Contenido |
| --- | --- |
| [01_arquitectura.md](01_arquitectura.md) | Visión general del sistema, componentes y diagrama de alto nivel. |
| [02_pipeline_flujo.md](02_pipeline_flujo.md) | Detalle del flujo de ejecución `job()` paso a paso. |
| [03_referencia_modulos.md](03_referencia_modulos.md) | Referencia función por función de cada módulo Python. |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Esquemas de los DataFrames de salida, tablas de Excel y base de datos local. |
| [05_configuracion_despliegue.md](05_configuracion_despliegue.md) | Variables de entorno, dependencias, ejecución local y CI/CD. |
| [06_catalogo_tipos_trabajo.md](06_catalogo_tipos_trabajo.md) | Catálogo de tipos de trabajo, subtipos y nomenclatura de columnas. |
| [07_processor_detalle.md](07_processor_detalle.md) | Detalle técnico exhaustivo del módulo de normalización `processor.py`. |

> El detalle exhaustivo del módulo de normalización (`processor.py`) está en
> [07_processor_detalle.md](07_processor_detalle.md). Ese documento integra y actualiza al
> antiguo `documentacion_processor.md` (ya eliminado), corrigiendo su descripción para que
> refleje el comportamiento vigente del código.

## Resumen ejecutivo

- **Origen de datos**: API de Connecteam (formulario `FORM_ID = 15540738`).
- **Destino**: `Terreno.xlsx` en SharePoint, vía Microsoft Graph API.
- **Deduplicación**: base de datos SQLite local `form_entries.db` versionada en el repositorio.
- **Orquestación**: GitHub Actions, de lunes a sábado a las 09:00 UTC.
- **Lenguaje**: Python 3.11.9.
- **Directorio de trabajo de la aplicación**: `trabajos_terreno/`.

## Convenciones de esta documentación

- Las rutas de archivo se expresan relativas a la raíz del repositorio salvo indicación contraria.
- Las referencias a líneas de código corresponden al estado del repositorio al momento de redactar este documento y pueden desplazarse con cambios posteriores.
- Lenguaje técnico, sin elementos decorativos.
