# 03 — Referencia de módulos

Referencia función por función de cada módulo de `trabajos_terreno/`. El detalle
exhaustivo de `processor.py` está en [07_processor_detalle.md](07_processor_detalle.md);
aquí se resume su interfaz.

---

## `config.py`

Carga las variables de entorno mediante `python-dotenv` y define constantes globales.

| Símbolo | Tipo | Descripción |
| --- | --- | --- |
| `SHAREPOINT_USER`, `SHAREPOINT_PASSWORD`, `SHAREPOINT_SITE`, `SHAREPOINT_NAME_SITE`, `SHAREPOINT_DOC_LIBRARY` | `str` | Credenciales SharePoint legacy. Definidas pero no todas en uso. |
| `CONNECTEAM_API_KEY` | `str` | API key de Connecteam (de entorno). |
| `FORM_ID` | `str` | Identificador del formulario, fijado a `"15540738"`. |
| `EXCEL_URL` | `str` | URL completa de Graph API del archivo `Terreno.xlsx` de destino. |
| `RUN_INTERVAL_MINUTES` | `int` | Constante legacy (valor `0`). |

Efecto colateral de import: fija `os.environ['SSL_CERT_FILE']` a `certifi.where()` para
asegurar la cadena de certificados TLS.

---

## `connecteam_api.py`

Cliente REST de Connecteam. Todas las funciones reciben la API key como argumento y
devuelven el JSON deserializado.

| Función | Endpoint | Retorno |
| --- | --- | --- |
| `all_submission(API_key)` | `GET /forms/v1/forms/{FORM_ID}/form-submissions?limit=100&offset=0` | JSON con las últimas 100 submissions. |
| `form_structure(API_key)` | `GET /forms/v1/forms/{FORM_ID}` | JSON con la estructura del formulario. |
| `filter_submissions(API_key)` | `GET .../form-submissions` con rango de fechas | JSON filtrado por fechas. **Legacy/debug**: la fecha base está fijada a `date(2025, 11, 12)`; no se usa en el flujo principal. |
| `user(API_key, user_id)` | `GET /users/v1/users?userIds={user_id}&userStatus=active` | `str` con `firstName + ' ' + lastName`. |

> `user` lanza excepción (índice fuera de rango) si el usuario no está activo o no existe.
> El llamador (`processor.process_entrys`) la captura y asigna `"Usuario no encontrado"`.

---

## `data_processing.py`

### `ordenar_respuestas(estructura, respuestas) -> pd.DataFrame`

Aplana el JSON de submissions a un DataFrame (una fila por OT, una columna por título de
pregunta).

- **Mapeo recursivo** de `questionId` a título, incluyendo preguntas dentro de bloques
  `group`.
- **Extracción por `questionType`**:
  - `openEnded` → `value`.
  - `multipleChoice` → textos seleccionados unidos por coma.
  - `yesNo` → `selectedIndex == 0` produce `"Sí"`, `== 1` produce `"No"` (convención invertida respecto a lo habitual).
  - `datetime` → objeto `date` en zona `America/Santiago`.
  - `image` → lista de URLs.
  - `signature` → `"Firma Capturada"` o `"Sin Firma"`.
  - `rating` → `ratingValue`.
  - `description` → `None`.
- **Filtros de validez**: descarta respuestas `wasHidden=True`, y `wasSubmittedEmpty=True`
  solo si además no tienen ningún dato real (`_tiene_dato`).
- Columnas base por fila: `#` (número de OT), `user` (ID del técnico), `fecha_envio`.
- Devuelve un DataFrame vacío si no hay submissions.

### `check_new_sub(ordered_responses) -> pd.DataFrame | bool | list`

Identifica OT no procesadas previamente y registra las nuevas en SQLite.

- Construye el conjunto de IDs de OT presentes en el DataFrame.
- Consulta `processed_entries` en `form_entries.db` (ruta resuelta relativa al archivo
  del módulo) para hallar IDs ya procesados.
- Inserta los IDs nuevos con `INSERT OR IGNORE`.
- **Retornos**: DataFrame con las OT nuevas; `False` si no hay nuevas; `[]` si ocurre un
  error de SQLite. El llamador valida con `isinstance(..., pd.DataFrame)`.

> La inserción ocurre antes de confirmar la carga a SharePoint (ver
> [02_pipeline_flujo.md](02_pipeline_flujo.md), sección de manejo de errores).

---

## `processor.py`

### `process_entrys(ordered_responses, API_key_c) -> (pd.DataFrame, pd.DataFrame)`

Núcleo de normalización. Recibe el DataFrame de OT y produce:

- `df_final_terreno`: registros atómicos a nivel equipo × punto × tipo de trabajo.
- `df_final_inspeccion`: rondas de inspección, expandidas por punto visitado.

Flujo resumido:

1. Por cada OT, elimina columnas nulas (`dropna`) y resuelve el nombre del técnico vía API.
2. Si `Tipo de visita realizada == '(R) Ronda diaria de Inspección'`, acumula la fila en
   inspecciones y continúa.
3. En caso contrario, detecta los puntos visitados (primer dígito de cada columna),
   resuelve proyecto y punto de monitoreo, cuenta instancias por tipo de trabajo y genera
   un registro por equipo/tipo.
4. Concatena inspecciones, expande la columna `Puntos visitados` y ordena ambos DataFrames
   por fecha descendente.

Tipos de trabajo con rama de procesamiento propia: `R` (y su variante `E`), `MC`, `CF`,
`I`, `MP`, `SO`, `LT`, `C`, `G`. Ver
[06_catalogo_tipos_trabajo.md](06_catalogo_tipos_trabajo.md) y
[07_processor_detalle.md](07_processor_detalle.md).

---

## `excel_manager.py`

### `modify_excel_file(resumen, sheet_name, table_name, sharepoint_client)`

1. Descarga `Terreno.xlsx` desde `EXCEL_URL`.
2. Lo abre con `openpyxl`, selecciona la hoja `sheet_name` y la tabla `table_name`.
3. Determina la primera fila de datos (justo debajo del header de la tabla) e **inserta**
   ahí las filas nuevas con `insert_rows`, desplazando hacia abajo los datos existentes
   (los registros más recientes quedan arriba).
4. Escribe `resumen` (lista de listas) celda por celda a partir de la columna inicial de la
   tabla; a las celdas con valores `date`/`datetime` les aplica formato `DD/MM/YY`.
5. Actualiza `tabla.ref` para incluir las filas nuevas.
6. Sube el libro modificado de vuelta a SharePoint.

Captura excepciones e imprime el error; no relanza.

### `send_data(df, sheet, table, sharepoint_client)`

Convierte el DataFrame a lista de listas (`df.values.tolist()`) y llama a
`modify_excel_file` solo si la lista no está vacía.

> Riesgo conocido: el orden de las columnas del DataFrame debe coincidir con el orden de
> las columnas de la tabla de Excel, ya que la escritura es posicional (a partir de la
> columna inicial de la tabla). No hay validación de cabeceras.

---

## `conn_sharepoint.py`

Funciones de bajo nivel sobre Microsoft Graph.

| Función | Descripción |
| --- | --- |
| `get_auth_token()` | Obtiene un token con MSAL `ConfidentialClientApplication` (client credentials, scope `.default`). Lee `MS_TENANT`, `MS_CLIENT_ID`, `MS_CLIENT_SECRET`. |
| `get_file_from_sharepoint(url, token)` | `GET` con cabecera `Authorization: Bearer`. Devuelve el objeto `Response`. |
| `upload_file_to_sharepoint(url, token, file_content, content_type)` | `PUT` con el contenido del archivo. `content_type` por defecto es el de un libro `.xlsx`. |

---

## `sharepoint_client.py`

### `class Sharepoint`

Fachada orientada a objetos. En `__init__` obtiene y almacena el token.

| Método | Descripción |
| --- | --- |
| `download_file(file_name, folder_name='')` | Devuelve el contenido binario del archivo, o `None` ante error. `file_name` es la URL completa de Graph. |
| `upload_file(file_name, content_stream, content_type=None, folder_name='')` | Sube el contenido del stream. Detecta el caso de archivo bloqueado (`SPFileLockException` / `423 Locked`) e imprime un aviso. |

> Observación: el manejo del caso "archivo bloqueado" imprime y espera 5 segundos, pero no
> implementa un reintento efectivo de la subida.

---

## `main.py` y `main_practice.py`

Puntos de entrada descritos en [02_pipeline_flujo.md](02_pipeline_flujo.md). Ambos
importan `schedule` y `time` (importaciones sin uso efectivo en el flujo actual).
