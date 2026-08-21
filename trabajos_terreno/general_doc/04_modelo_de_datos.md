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

Ordenamiento: descendente por `Fecha visita` (más reciente primero). Como las filas se
insertan al inicio de la tabla, el resultado queda cronológicamente coherente en el dashboard.

> La escritura en Excel es **por nombre de columna**, no posicional (cambió en el commit
> `20b58ec`). Lo que debe coincidir es el *nombre* de cada columna con el encabezado de la
> tabla `OTS`; el orden es indiferente. Una columna sin encabezado correspondiente se omite
> con una advertencia por consola.

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

## 5. DataFrame de salida: `data_residuos`

Destino: hoja `Residuos`, tabla `Residuos`. Origen: la sección **"Gestión de residuos"** del
formulario (bloque `description` con id `12dc03fc-3313-0b62-bd66-f43411c659e5`, seguido de las
preguntas de la sección).

Grano: **una fila por OT × categoría de residuo declarada**. La sección se responde una sola vez
por OT, no por punto ni por equipo, de ahí que tenga tabla propia: incluirla en `data_terreno`
replicaría el mismo retiro en todas las filas de la OT y produciría doble conteo al consolidar.
La llave para cruzar con `OTS` es `OT`.

Las cuatro categorías (grupos del formulario) están declaradas en `CATEGORIAS_RESIDUOS`
(`processor.py`), y los encabezados en `HEADERS_RESIDUOS`:

| Columna | Tipo | Origen / Notas |
| --- | --- | --- |
| `OT` | `str` | `'III-' + número de OT`. |
| `Técnico` | `str` | Nombre resuelto vía API. |
| `Fecha envío` | `str` | Columna `fecha_envio`. |
| `Fecha visita` | `date` | Columna `Fecha visita ` (espacio final en el origen). |
| `Contrato` | `str` | Columna global. |
| `Cliente` | `str` | `Nombre del Cliente`. |
| `Tipo de visita` | `str` | `Tipo de visita realizada`. Cubre trabajos y rondas de inspección. |
| `Retiro de residuos` | `str` | `¿Hubo residuos?` (Sí/No). Si no es `'Sí'`, no se emite fila. |
| `Tipos declarados` | `str` | `Indique el tipo de residuo generado` (multiselección, unida por `', '`). |
| `Categoría` | `str \| None` | `Plásticos y electrónicos`, `Electrónicos`, `Residuos peligrosos` o `Desechos`. `None` cuando se declaró retiro sin llenar ninguna categoría. |
| `Detalle` | `str \| None` | `Detalle de residuo` / `Indicar tipo de RAEE` / `Indicar tipo de residuo`, según categoría. |
| `N° de serie` | `str \| None` | `Número serial`. Solo Electrónicos y Residuos peligrosos. |
| `Falla presentada` | `str \| None` | Solo Electrónicos. |
| `Cantidad` | `str \| None` | Texto libre (p.ej. "Bolsa chica", "1 unidad"). |
| `Destino` | `str \| None` | Pregunta `yesNo` en el formulario, se registra como Sí/No. |

> **Colisión de títulos**: los cuatro grupos repiten los títulos `Cantidad`, `Destino`,
> `Detalle de residuo` y `Número serial`. Como `ordenar_respuestas` indexa las columnas por
> título, antes cada grupo sobreescribía al anterior y solo sobrevivía el último. Hoy, a las
> preguntas que viven dentro de un grupo y cuyo título se repite en el formulario se les
> antepone el título del grupo con la convención ` | ` (`Electrónicos | Cantidad`). Las
> preguntas de nivel raíz no se tocan.

Las categorías no declaradas llegan con `wasHidden=True` y vacías, así que no generan columnas
ni filas.

## 6. Destino en SharePoint

| Atributo | Valor |
| --- | --- |
| Archivo | `Terreno.xlsx` |
| Ruta | `Customer Experience/Modelos de datos/Modelo -  Dashboard clientes/` |
| Acceso | Microsoft Graph API (`EXCEL_URL` en `config.py`) |
| Hoja / Tabla terreno | `Terreno` / `OTS` |
| Hoja / Tabla inspección | `Inspección` / `Ronda` |
| Hoja / Tabla residuos | `Residuos` / `Residuos` |

La escritura es incremental: se insertan filas nuevas al inicio de la tabla nombrada (debajo
del header, desplazando los datos previos) y se expande la referencia (`tabla.ref`) para
incluirlas. No se sobrescriben filas existentes.

La tabla `Residuos` la crea el propio código en la primera corrida:
`send_data(..., headers_si_falta=HEADERS_RESIDUOS)` invoca `_asegurar_hoja_y_tabla`
(`excel_manager.py`), que registra un objeto `Table` completo para que Excel no marque el
archivo como dañado. La operación es idempotente. **No hay que crear nada a mano.**

Estado verificado de `Terreno.xlsx` (agosto 2026):

- La hoja `Residuos` **ya existe pero está vacía** (`A1:A1`, sin encabezados ni tabla
  nombrada). `_asegurar_hoja_y_tabla` la reutiliza y le agrega los encabezados y la tabla.
- Si la fila 1 de la hoja trajera encabezados **distintos** a `HEADERS_RESIDUOS` y no
  existiera la tabla, la escritura se aborta con un `ValueError` explicativo en vez de pisar
  lo que haya. La fila 1 vacía es la condición para que el código la genere.
- La tabla `OTS` arrastra dos columnas vestigiales del enfoque abandonado, `Residuos` y
  `Tipo de residuo` (posiciones 23-24), que quedan permanentemente vacías: el dato de
  residuos vive en su propia tabla. Se pueden eliminar de la planilla sin afectar el
  pipeline (la escritura es por nombre de columna).
- El libro tiene además una hoja `Análisis MC 2026` con ~105 fórmulas de matriz. Se verificó
  que sobreviven al round-trip de openpyxl que hace `modify_excel_file`.
