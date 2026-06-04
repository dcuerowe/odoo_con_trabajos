# 04 — Modelo de datos

## 1. Base de datos local de deduplicación

Archivo: `trabajos_terreno/form_entries.db` (SQLite). **Versionado en el repositorio.**

```sql
CREATE TABLE processed_entries (
    entry_id INTEGER PRIMARY KEY
);
```

- Una sola tabla, una sola columna. `entry_id` corresponde al número de OT (`#`/`entryNum`).
- Funciona como registro de OT ya enviadas a SharePoint.
- El workflow de GitHub Actions hace `git add` + `commit` + `push` de este archivo al final
  de cada ejecución, de modo que la corrida siguiente parta del estado actualizado.
- No debe borrarse ni resetearse sin entender que ello provocaría el reprocesamiento (y
  posible duplicación) de OT en SharePoint.

## 2. DataFrame intermedio: salida de `ordenar_respuestas`

Una fila por OT. Columnas fijas: `#`, `user`, `fecha_envio`. El resto de columnas son
dinámicas: su nombre es el título de la pregunta en Connecteam. Las preguntas por punto
llevan prefijo numérico (`1.*`, `2.*`, ...). Ejemplos de columnas:

```
#                                  -> número de OT
user                               -> ID del técnico (luego resuelto a nombre)
fecha_envio                        -> dd-mm-yyyy de envío
Tipo de visita realizada
Contrato
Causa visita
Nombre del Cliente
1.1 Punto de monitoreo
1.2 Tipo de trabajo a realizar
1.2.1 MC | Modelo
1.2.1 MC | N° de serie
...
```

## 3. DataFrame de salida: `data_terreno`

Destino: hoja `Terreno`, tabla `OTS` de `Terreno.xlsx`. Una fila por equipo intervenido
× punto × tipo de trabajo.

| Columna | Tipo | Origen / Notas |
| --- | --- | --- |
| `OT` | `str` | `'III-' + número de OT`. |
| `Técnico` | `str` | Nombre resuelto vía API. |
| `Contrato` | `str` | Columna global de la OT. |
| `Causa visita` | `str` | Columna global. |
| `Proyecto` | `str` | Extraído de `[...]` en el nombre del punto, o ingresado manualmente. |
| `Asset` | `str` | Punto de monitoreo (sin la porción `[Proyecto]`). |
| `Tipo de trabajo` | `str` | Identificador del tipo: `MC`, `MP`, `I`, `R`, `E`, `CF`, `SO`, `LT`, `C`, `G`. |
| `Fecha visita` | `date` | Columna `Fecha visita ` (con espacio final en el origen). |
| `Cliente` | `str` | `Nombre del Cliente`. |
| `Resolución visita` | `str` | `{i}.3 Resolución de visita`. |
| `Calidad del Servicio` | `str` | Columna global. |
| `PT (Permiso de trabajo)` | `str` | Documento de seguridad. |
| `DET (Análisis de Riesgos)` | `str` | Documento de seguridad. |
| `Cinco Pasos para Trabajar Seguro` | `str` | Documento de seguridad. |
| `Charla de 5 Minutos` | `str` | Documento de seguridad. |
| `Check List de Camioneta/ Somnolencia` | `str` | Documento de seguridad. |
| `AST` | `str` | Documento de seguridad. |
| `Observación` | `str \| None` | Específico del equipo. |
| `Equipo` | `str \| None` | Tipo de equipo/activo intervenido. |
| `Modelo` | `str \| None` | Modelo del equipo. |
| `N° serie` | `str \| None` | Número de serie. |
| `Alcance` | `str \| None` | Motivo/alcance específico del tipo de trabajo. |

Ordenamiento: descendente por `Fecha visita` (más reciente primero), para que al insertar
al final de la tabla queden cronológicamente coherentes en el dashboard.

> El orden de las columnas de este DataFrame debe coincidir con el orden de columnas de la
> tabla `OTS` en Excel, dado que la escritura es posicional.

## 4. DataFrame de salida: `data_inspeccion`

Destino: hoja `Inspección`, tabla `Ronda`. Se construye concatenando las filas cuyo
`Tipo de visita realizada` es `'(R) Ronda diaria de Inspección'`, conservando sus columnas
originales (títulos de pregunta del formulario).

Transformaciones aplicadas:

- **Expansión por puntos visitados**: si la columna `Puntos visitados` contiene varios
  puntos separados por coma, la fila se replica en N filas, una por punto.
- **Eliminación de columna**: se elimina `Fotos ` (con espacio final).
- **Ordenamiento**: descendente por `Fecha visita ` (con espacio final).

> A diferencia de `data_terreno`, las columnas de inspección no se renombran a un esquema
> fijo: dependen directamente de los títulos del formulario. Cambios en esos títulos
> impactan directamente la tabla `Ronda`.

## 5. Destino en SharePoint

| Atributo | Valor |
| --- | --- |
| Archivo | `Terreno.xlsx` |
| Ruta | `Customer Experience/Modelos de datos/Modelo -  Dashboard clientes/` |
| Acceso | Microsoft Graph API (`EXCEL_URL` en `config.py`) |
| Hoja / Tabla terreno | `Terreno` / `OTS` |
| Hoja / Tabla inspección | `Inspección` / `Ronda` |

La escritura es incremental: se anexan filas tras la última fila de la tabla nombrada y se
expande la referencia (`tabla.ref`) para incluirlas. No se sobrescriben filas existentes.
