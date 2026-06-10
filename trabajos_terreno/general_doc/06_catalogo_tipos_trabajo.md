# 06 — Catálogo de tipos de trabajo y nomenclatura

## 1. Nomenclatura de columnas del formulario

Connecteam genera columnas con una estructura jerárquica. El patrón general es:

```
{punto}.{sección}.{instancia} {tipo} ({subtipo}) | {campo}
```

| Columna de ejemplo                 | Punto | Sección | Instancia | Tipo | Subtipo | Campo              |
| ---------------------------------- | ----- | -------- | --------- | ---- | ------- | ------------------ |
| `1.1 Punto de monitoreo`         | 1     | 1        | —        | —   | —      | Punto de monitoreo |
| `1.2 Tipo de trabajo a realizar` | 1     | 2        | —        | —   | —      | Tipo de trabajo    |
| `1.2.1 MC \| Modelo`              | 1     | 2        | 1         | MC   | —      | Modelo             |
| `1.2.2 MP (I) \| N° de serie`    | 1     | 2        | 2         | MP   | I       | N° de serie       |
| `2.2.1 R (E) \| Modelo`           | 2     | 2        | 1         | R    | E       | Modelo             |

El procesador detecta los puntos visitados leyendo el **primer carácter** del nombre de
cada columna no nula. El conteo de instancias por tipo se obtiene contando los prefijos
únicos que contienen el patrón ` {TIPO} |` o ` {TIPO} ({subtipo}) |`.

## 2. Tipos de trabajo

| ID     | Significado                            | Rama en `processor.py`           | Datos de equipo                       |
| ------ | -------------------------------------- | ---------------------------------- | ------------------------------------- |
| `MC` | Mantención Correctiva                 | Sí                                | Sí                                   |
| `MP` | Mantención Preventiva                 | Sí (subtipos `T`, `I`)        | Sí                                   |
| `I`  | Instalación                           | Sí (subtipos `I`, `T`, `C`) | Sí                                   |
| `R`  | Reemplazo (Extracción + Instalación) | Sí (subtipos `E`, `I`)        | Sí                                   |
| `E`  | Solo Extracción                       | Generada dentro de la rama `R`   | Sí                                   |
| `CF` | Configuración / Ajustes               | Sí                                | Sí                                   |
| `SO` | Solicitud de Obra                      | Sí                                | Parcial (solo Alcance y Observación) |
| `LT` | Levantamiento Técnico                 | Sí                                | No                                    |
| `C`  | Capacitación                          | Sí                                | No                                    |
| `G`  | Garantía                              | Sí                                | No                                    |

### Subtipos

| Tipo   | Subtipos            | Traducción                                        |
| ------ | ------------------- | -------------------------------------------------- |
| `MP` | `T`, `I`        | `T`=Tablero, `I`=Dispositivo                   |
| `I`  | `I`, `T`, `C` | `I`=dispositivo, `T`=tablero, `C`=Categoría |
| `R`  | `E`, `I`        | `E`=Extracción, `I`=Instalación              |

## 3. Resumen por tipo de trabajo

- **`R` (Reemplazo/Extracción)**: rama más compleja. Itera sobre `R_type = ['E', 'I']`
  generando un registro por equipo de reemplazo, y adicionalmente procesa extracciones
  independientes (`conteo_instancias_E`) registradas con tipo `"E"`. Campos: modelo, tipo,
  serie, observación, motivo (reemplazo/extracción) y destino (solo en extracción).
  En la salida, `Tipo de trabajo` se registra como el **subtipo** (`E`/`I`), no como el
  literal `R` (ver [07_processor_detalle.md](07_processor_detalle.md) §10.1).
- **`MC`**: itera sobre `conteo_instancias_MC`. `Alcance = None`. El campo "¿Equipo
  operativo tras trabajos?" se lee pero no se propaga a la salida.
- **`CF`**: estructura análoga a MC; `Alcance` se lee de `Tipo de Ajuste`.
- **`I` (Instalación)**: doble iteración sobre `I_type = ['I', 'T', 'C']` e instancias. Para
  dispositivos el `Alcance` se fija como `'IH | Habilitación de equipo'`; para tableros se
  lee de `Alcance de la intervención`. Usa `.get(...)` para tolerar campos ausentes en
  submissions antiguas y en el subtipo `C` (Categoría).
- **`MP` (Mantención Preventiva)**: doble iteración sobre `MP_type = ['T', 'I']` e
  instancias. Etiquetas de columna adaptadas con `MP_translate`. `Alcance = None`.
- **`SO`**: registra `Alcance` (Tipo de solicitud) y `Observación`; `Equipo`, `Modelo`,
  `N° serie` son `None`.
- **`LT`, `C`, `G`**: registro simple sin datos de equipo (todos los campos de equipo
  `None`).

## 4. Resolución de proyecto y punto

- **Punto registrado**: el nombre del punto incluye el proyecto entre corchetes
  (`"Punto ABC [Proyecto XYZ]"`). El proyecto se extrae con `re.search(r"\[([^\]]*)\]", ...)`
  y se elimina del nombre del punto.
- **Punto "No encontrado"**: se usa la columna `{i} Proyecto` y el nombre ingresado
  manualmente en `{i}.1 Indicar nombre del punto`. Si la resolución falla, se asignan
  valores por defecto y el punto se omite con `continue`.

## 5. Notas de comportamiento (correcciones respecto a documentación antigua)

El antiguo `documentacion_processor.md` (ya integrado en
[07_processor_detalle.md](07_processor_detalle.md)) describía comportamientos que **no
están implementados** en el código vigente. Tras la actualización quedan así documentados:

| Comportamiento descrito en la versión antigua                                                          | Estado real en `processor.py`                                                                                         |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Reclasificación automática de `R` a `CI` ("Calibración programada" / "Retorno de calibración"). | **No implementada.** `trabajo_R = t`; el `Tipo de trabajo` queda como subtipo `E`/`I`.                    |
| Bloque `elif id == 'CI'` con equipo hardcoded `"Sonda multiparamétrica"`.                          | **No existe** rama `CI` en el código actual.                                                                   |
| `CI` como tipo de trabajo procesable.                                                                 | `CI` no está en `id_tipo_de_trabajo` ni tiene rama propia; `conteo_instancias_CI` se calcula pero no se consume. |
| Subtipo `I (C)` (Categoría) descrito brevemente.                                                     | Presente en el código (`I_type` incluye `C`), con manejo defensivo vía `.get`.                                  |
