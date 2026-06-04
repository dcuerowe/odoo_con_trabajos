# 03 — Casos de prueba

Convención de identificadores: `TC-<MÓDULO>-<NN>`. Severidad: Alta / Media / Baja.

---

## A. `ordenar_respuestas` (data_processing)

### TC-OR-01 — Extracción de respuesta openEnded
- **Severidad**: Media
- **Precondición**: Estructura con una pregunta `openEnded` y una submission con `value`.
- **Pasos**: Invocar `ordenar_respuestas(estructura, respuestas)`.
- **Resultado esperado**: La columna con el título de la pregunta contiene el texto de `value`.

### TC-OR-02 — Mapeo yesNo invertido
- **Severidad**: Media
- **Pasos**: Submission con `selectedIndex = 0` y otra con `selectedIndex = 1`.
- **Resultado esperado**: `0` produce `"Sí"`; `1` produce `"No"`.

### TC-OR-03 — Fecha en zona America/Santiago
- **Severidad**: Media
- **Pasos**: Pregunta `datetime` con un `timestamp` conocido.
- **Resultado esperado**: Se devuelve un objeto `date` convertido a `America/Santiago` (no `datetime`, no string ambiguo mm/dd).

### TC-OR-04 — Pregunta anidada en bloque group
- **Severidad**: Alta
- **Pasos**: Estructura con un `group` que contiene preguntas; submission con `questionType='group'` y `answers` internas.
- **Resultado esperado**: Cada pregunta anidada aparece como columna usando su título mapeado recursivamente.

### TC-OR-05 — Respuesta oculta (wasHidden) se descarta
- **Severidad**: Media
- **Pasos**: Answer con `wasHidden=True` y un `value`.
- **Resultado esperado**: La columna no se crea (valor `None`, omitido).

### TC-OR-06 — wasSubmittedEmpty con dato real se conserva
- **Severidad**: Alta
- **Pasos**: Answer con `wasSubmittedEmpty=True` pero con `value` no vacío.
- **Resultado esperado**: El valor se conserva (no se descarta), validando `_tiene_dato`.

### TC-OR-07 — multipleChoice múltiple
- **Severidad**: Baja
- **Pasos**: Answer con varios `selectedAnswers`.
- **Resultado esperado**: Textos unidos por `", "`.

### TC-OR-08 — Sin submissions
- **Severidad**: Baja
- **Pasos**: `respuestas` sin `formSubmissions`.
- **Resultado esperado**: Se devuelve un `pd.DataFrame` vacío.

### TC-OR-09 — image y signature
- **Severidad**: Baja
- **Pasos**: Answers de tipo `image` (con URLs) y `signature` (con/sin imágenes).
- **Resultado esperado**: `image` produce lista de URLs; `signature` produce `"Firma Capturada"` o `"Sin Firma"`.

---

## B. `check_new_sub` (data_processing)

> Todas las pruebas operan sobre una **copia temporal** de `form_entries.db`.

### TC-CN-01 — Detección de OT nueva
- **Severidad**: Alta
- **Precondición**: Base sin el ID de la OT.
- **Pasos**: Invocar `check_new_sub` con un DataFrame que contiene esa OT.
- **Resultado esperado**: Se devuelve un DataFrame con la OT nueva y su ID queda insertado en `processed_entries`.

### TC-CN-02 — OT ya procesada se omite
- **Severidad**: Alta
- **Precondición**: ID ya presente en la base.
- **Resultado esperado**: La OT no aparece en el resultado.

### TC-CN-03 — Sin OT nuevas
- **Severidad**: Media
- **Pasos**: Todos los IDs ya están en la base.
- **Resultado esperado**: Retorna `False` e imprime "No hay nuevas OTs para procesar".

### TC-CN-04 — Idempotencia de inserción
- **Severidad**: Media
- **Pasos**: Ejecutar `check_new_sub` dos veces con la misma OT nueva.
- **Resultado esperado**: La segunda ejecución no la detecta como nueva; no hay duplicados en la tabla (clave primaria + `INSERT OR IGNORE`).

### TC-CN-05 — Error de base de datos
- **Severidad**: Baja
- **Pasos**: Apuntar a una ruta inválida o tabla inexistente.
- **Resultado esperado**: Captura `sqlite3.Error`, imprime traceback y retorna `[]`.

---

## C. `process_entrys` (processor) — por tipo de trabajo

> Mock obligatorio de `connecteam_api.user` para evitar la red.

### TC-PE-01 — Ronda de inspección se enruta a inspección
- **Severidad**: Alta
- **Pasos**: OT con `Tipo de visita realizada = '(R) Ronda diaria de Inspección'`.
- **Resultado esperado**: La fila va a `df_final_inspeccion`, no a `df_final_terreno`.

### TC-PE-02 — Expansión por puntos visitados
- **Severidad**: Alta
- **Pasos**: Inspección con `Puntos visitados = "Punto A, Punto B, Punto C"`.
- **Resultado esperado**: 3 filas en `df_final_inspeccion`, una por punto; columna `Fotos ` eliminada.

### TC-PE-03 — Mantención Correctiva (MC)
- **Severidad**: Alta
- **Pasos**: OT con un punto y una instancia `1.2.1 MC | ...`.
- **Resultado esperado**: Un registro en `df_final_terreno` con `Tipo de trabajo = 'MC'`, `Alcance = None`, y los campos Modelo/Equipo/N° serie/Observación poblados.

### TC-PE-04 — Mantención Preventiva (MP) con subtipos
- **Severidad**: Alta
- **Pasos**: OT con `MP (T)` y `MP (I)`.
- **Resultado esperado**: Un registro por cada subtipo/instancia; etiquetas de campo resueltas con `MP_translate` (Tablero/Dispositivo); `Alcance = None`.

### TC-PE-05 — Instalación (I) dispositivo, tablero y categoría
- **Severidad**: Alta
- **Pasos**: OT con `I (I)`, `I (T)` e `I (C)`.
- **Resultado esperado**: Dispositivo con `Alcance = 'IH | Habilitación de equipo'`; tablero con `Alcance` leído del formulario; categoría tolerada vía `.get` sin error por campos ausentes.

### TC-PE-06 — Reemplazo completo (R: E + I)
- **Severidad**: Alta
- **Pasos**: OT con `R (E)` y `R (I)`.
- **Resultado esperado**: Registros con `Tipo de trabajo` correspondiente al subtipo; campos modelo, tipo, serie, motivo y destino (solo en E) poblados.

### TC-PE-07 — Solo extracción (E)
- **Severidad**: Media
- **Pasos**: OT con columnas `{i}.2.{n} E | ...` sin reemplazo.
- **Resultado esperado**: Registro con `Tipo de trabajo = 'E'` y motivo de extracción.

### TC-PE-08 — Configuración/Ajustes (CF)
- **Severidad**: Media
- **Resultado esperado**: `Tipo de trabajo = 'CF'`, `Alcance` leído de `Tipo de Ajuste`.

### TC-PE-09 — Solicitud de Obra (SO)
- **Severidad**: Media
- **Resultado esperado**: `Tipo de trabajo = 'SO'`, `Alcance` = Tipo de solicitud, `Equipo/Modelo/N° serie = None`.

### TC-PE-10 — Tipos simples LT / C / G
- **Severidad**: Baja
- **Resultado esperado**: Un registro por tipo con todos los campos de equipo en `None`.

### TC-PE-11 — Resolución de proyecto desde corchetes
- **Severidad**: Alta
- **Pasos**: Punto = `"Estación Norte [Proyecto XYZ]"`.
- **Resultado esperado**: `Proyecto = 'Proyecto XYZ'`, `Asset = 'Estación Norte'`.

### TC-PE-12 — Punto "No encontrado" ingresado manualmente
- **Severidad**: Media
- **Pasos**: `{i}.1 Punto de monitoreo = "No encontrado"` con `{i}.1 Indicar nombre del punto` y `{i} Proyecto`.
- **Resultado esperado**: El nombre manual reemplaza a "No encontrado" y el proyecto se toma de `{i} Proyecto`.

### TC-PE-13 — Prefijo OT y nombre de técnico
- **Severidad**: Media
- **Resultado esperado**: `OT` con prefijo `III-`; `Técnico` igual al nombre resuelto (o `"Usuario no encontrado"` ante fallo de la API).

### TC-PE-14 — Múltiples puntos en una OT
- **Severidad**: Alta
- **Pasos**: OT con columnas `1.*` y `2.*`.
- **Resultado esperado**: Registros generados para ambos puntos, con su proyecto y asset respectivos.

### TC-PE-15 — Ordenamiento descendente por fecha
- **Severidad**: Baja
- **Resultado esperado**: `df_final_terreno` y `df_final_inspeccion` ordenados por fecha descendente.

### TC-PE-16 — Límite de 9 puntos (caso límite)
- **Severidad**: Media
- **Pasos**: OT con un punto cuyo prefijo sería de dos dígitos (`10.*`).
- **Resultado esperado**: Se documenta que `col[0]` lo mapea a `1`, colisionando con el punto 1. Confirma la limitación conocida; sirve de regresión si se corrige.

---

## D. `modify_excel_file` / `send_data` (excel_manager)

> Operan sobre una copia local de `Terreno.xlsx`; `download_file`/`upload_file` simulados con disco.

### TC-EX-01 — Inserción incremental en tabla OTS
- **Severidad**: Alta
- **Pasos**: `modify_excel_file` con N filas hacia hoja `Terreno`, tabla `OTS`.
- **Resultado esperado**: Las N filas se anexan tras la última fila; `tabla.ref` se expande en N filas; no se sobrescriben datos previos.

### TC-EX-02 — Inserción en tabla Ronda
- **Severidad**: Media
- **Resultado esperado**: Análogo a TC-EX-01 para hoja `Inspección`, tabla `Ronda`.

### TC-EX-03 — DataFrame vacío
- **Severidad**: Media
- **Pasos**: `send_data` con DataFrame vacío.
- **Resultado esperado**: No se invoca `modify_excel_file`; el archivo no cambia.

### TC-EX-04 — Alineación de columnas
- **Severidad**: Alta
- **Pasos**: Comparar el orden de columnas del DataFrame contra las cabeceras de la tabla `OTS`.
- **Resultado esperado**: Coincidencia posicional. Un desajuste evidencia el riesgo de escritura en columna incorrecta.

### TC-EX-05 — Fallo de descarga
- **Severidad**: Baja
- **Pasos**: `download_file` devuelve `None`.
- **Resultado esperado**: Se imprime "No se pudo descargar el archivo" y no se intenta subir.

---

## E. Clientes externos (connecteam_api / sharepoint_client)

### TC-API-01 — user resuelve nombre completo
- **Severidad**: Media
- **Pasos**: Simular respuesta con `firstName` y `lastName`.
- **Resultado esperado**: Devuelve `"Nombre Apellido"`.

### TC-API-02 — user con usuario inexistente
- **Severidad**: Media
- **Pasos**: Respuesta sin usuarios.
- **Resultado esperado**: Lanza excepción; en el contexto de `process_entrys` deriva en `"Usuario no encontrado"`.

### TC-SP-01 — Token de Graph
- **Severidad**: Media
- **Pasos**: Simular MSAL devolviendo `access_token`.
- **Resultado esperado**: `Sharepoint().token` queda poblado.

### TC-SP-02 — Archivo bloqueado (423)
- **Severidad**: Baja
- **Pasos**: `upload_file` ante error que contiene `423 Client Error: Locked`.
- **Resultado esperado**: Se imprime el aviso de bloqueo. Nota: el reintento no está implementado; el caso documenta el comportamiento real.

---

## F. Integración y sistema

### TC-INT-01 — Encadenamiento completo con API simulada
- **Severidad**: Alta
- **Pasos**: `ordenar_respuestas` → `check_new_sub` (SQLite temporal) → `process_entrys` con `user` simulado.
- **Resultado esperado**: Se obtienen `data_terreno` y `data_inspeccion` coherentes a partir del JSON de entrada.

### TC-INT-02 — OT marcada como procesada pese a fallo de carga
- **Severidad**: Alta
- **Pasos**: Forzar excepción en `send_data` tras `check_new_sub`.
- **Resultado esperado**: El ID quedó en la base aunque la carga falló. Confirma el riesgo documentado y la necesidad de reenvío manual.

### TC-SYS-01 — Reenvío manual con main_practice
- **Severidad**: Media
- **Pasos**: Ejecutar `main_practice.py`, indicar OT conocidas y un subconjunto de puntos.
- **Resultado esperado**: Solo los puntos seleccionados se procesan; las columnas globales se conservan; los datos llegan al Excel de prueba.
