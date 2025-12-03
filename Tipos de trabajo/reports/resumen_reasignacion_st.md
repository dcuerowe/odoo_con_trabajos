# Resumen de Reasignación de Categoría ST

Se ha procesado el universo de **195 registros** etiquetados como **ST (Soporte Técnico)** para reasignarlos a categorías más específicas.

## Distribución Propuesta

| Nueva Categoría | Cantidad de Registros | Porcentaje |
| :--- | :---: | :---: |
| **MP** (Mantenimiento Preventivo) | 79 | 40.5% |
| **MC** (Mantenimiento Correctivo) | 38 | 19.5% |
| **I** (Instalación e Integración) | 22 | 11.3% |
| **SO** (Solicitud Operativa) | 19 | 9.7% |
| **CF** (Configuración y Ajustes) | 14 | 7.2% |
| **LT** (Levantamiento Técnico) | 5 | 2.6% |
| *Revisar Manualmente* | 18 | 9.2% |
| **Total** | **195** | **100%** |

## Archivos Generados

1. **Detalle Completo (Excel):** `reasignacion_st_detallada.xlsx`
    * Contiene fila por fila la propuesta de cambio.
    * Campos: OT, Técnico, Proyecto, Asset, Tipo anterior, Tipo nuevo, Causa visita.
2. **Gráfico de Distribución:** `distribucion_reasignacion_st.png`
    * Visualización de barras con la nueva distribución.

## Criterios Utilizados

* **MP:** Se asignó cuando la causa incluía "preventivo", "mantención", "limpieza" o "contrastación".
* **MC:** Se asignó ante palabras clave como "falla", "reparación", "cambio", "revisión" (sin apellido preventivo) o "soporte".
* **I:** Se asignó para "instalación", "montaje", "habilitación" o "mejoramiento".
* **CF:** Se asignó para "configuración", "programación", "ajuste" o "firmware".
* **SO:** Se asignó para solicitudes específicas como "fotos", "caudal", "apoyo" o "visitas".
