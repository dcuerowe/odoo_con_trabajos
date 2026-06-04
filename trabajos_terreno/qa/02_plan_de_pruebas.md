# 02 — Plan de pruebas

## 1. Criterios de entrada

- Código compilable y ejecutable en Python 3.11.9.
- Dependencias instaladas (`requirements.txt`).
- Disponibilidad de fixtures de prueba (ver [04_datos_de_prueba.md](04_datos_de_prueba.md)).
- Copia de `form_entries.db` y de `Terreno.xlsx` en ubicaciones de prueba.

## 2. Criterios de salida

- Ejecución completa de los casos definidos en [03_casos_de_prueba.md](03_casos_de_prueba.md).
- Todos los casos de severidad alta y media en estado "Aprobado".
- Defectos de severidad alta resueltos o con excepción documentada y aprobada.

## 3. Cobertura por módulo

| Módulo | Funciones a cubrir | Tipo de prueba prioritario |
| --- | --- | --- |
| `data_processing.py` | `ordenar_respuestas`, `check_new_sub` | Unitario / Integración |
| `processor.py` | `process_entrys` (todas las ramas de tipo de trabajo) | Unitario |
| `excel_manager.py` | `modify_excel_file`, `send_data` | Integración con archivo local |
| `connecteam_api.py` | `all_submission`, `form_structure`, `user` | Unitario con HTTP simulado |
| `sharepoint_client.py` / `conn_sharepoint.py` | `download_file`, `upload_file`, token | Unitario con HTTP simulado |
| `main.py` / `main_practice.py` | Orquestación, manejo de errores | Integración / Manual |

## 4. Estrategia de simulación (mocking)

| Dependencia | Mecanismo recomendado |
| --- | --- |
| `requests.get` / `requests.put` (Connecteam y Graph) | Parchear con respuestas predefinidas (`unittest.mock` / `monkeypatch`). |
| `connecteam_api.user` (dentro de `processor`) | Parchear para devolver un nombre fijo y evitar la red. |
| `form_entries.db` | Apuntar a una base SQLite temporal (`tmp_path`) con el esquema `processed_entries`. |
| `EXCEL_URL` / SharePoint | Usar un `Terreno.xlsx` local; sustituir `download_file`/`upload_file` por lectura/escritura de disco. |

## 5. Secuencia de ejecución sugerida

1. Pruebas unitarias de `ordenar_respuestas` (extracción por tipo de pregunta).
2. Pruebas unitarias de `check_new_sub` sobre SQLite temporal.
3. Pruebas unitarias de `process_entrys` por tipo de trabajo.
4. Pruebas de integración del encadenamiento completo con API simulada.
5. Pruebas de `modify_excel_file` sobre archivo local.
6. Pruebas de sistema manuales con `main_practice.py` hacia destino de prueba.

## 6. Registro de resultados

Cada ejecución debe registrarse con: identificador del caso, build/commit, fecha, estado
(Aprobado / Fallido / Bloqueado), evidencia y defecto asociado si corresponde. Se sugiere
mantener una tabla de seguimiento por release junto al
[checklist](05_checklist_release.md).
