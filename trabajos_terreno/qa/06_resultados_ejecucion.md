# 06 — Resultados de ejecución de pruebas

## 1. Resumen

| Atributo | Valor |
| --- | --- |
| Fecha de ejecución | 2026-06-04 01:36 (-04, America/Santiago) |
| Comando | `python3 -m pytest tests/ -v` (desde `trabajos_terreno/qa/`) |
| Python | 3.14.0 |
| pytest | 9.0.3 |
| Dependencias clave | pandas 2.3.3, openpyxl 3.1.5 |
| Total de pruebas | 25 |
| Aprobadas | 25 |
| Fallidas | 0 |
| Errores | 0 |
| Omitidas | 0 |
| Duración | 0.20 s |

**Resultado global: APROBADO (25/25).**

> Nota de entorno: la ejecución se realizó con Python 3.14.0, superior a la versión de
> producción declarada (3.11.9). Las funciones bajo prueba no usan características
> específicas de versión, por lo que el resultado es representativo. Para una validación
> idéntica a producción, reejecutar con Python 3.11.9.

## 2. Infraestructura creada

Para ejecutar las pruebas se incorporó:

- `qa/tests/conftest.py` — inserta `trabajos_terreno/` en `sys.path` (imports planos) y
  expone fixtures de submissions y de filas de OT.
- `qa/tests/test_ordenar_respuestas.py` — casos TC-OR.
- `qa/tests/test_check_new_sub.py` — casos TC-CN, con SQLite temporal aislado.
- `qa/tests/test_process_entrys.py` — casos TC-PE, con `processor.user` simulado.
- `qa/tests/test_excel_manager.py` — casos TC-EX, con libro Excel local y cliente SharePoint simulado.

No se añadieron dependencias al proyecto: `pytest`, `pandas` y `openpyxl` ya estaban
disponibles en el entorno.

## 3. Aislamiento y protección de producción

- **Base de datos**: las pruebas de `check_new_sub` parchean `sqlite3.connect` del módulo
  para redirigir a una base temporal (`tmp_path`). Verificado tras la ejecución:
  `form_entries.db` de producción mantiene **244 filas** y no presenta cambios en git.
- **SharePoint**: ninguna prueba accede a la red. `download_file`/`upload_file` se sustituyen
  por un cliente simulado en memoria. El `Terreno.xlsx` de producción no se toca.
- **API Connecteam**: `processor.user` se reemplaza por un mock; no hay llamadas HTTP.

## 4. Detalle por caso

| ID | Prueba | Resultado |
| --- | --- | --- |
| TC-OR-01 | `test_tc_or_01_open_ended` | Aprobado |
| TC-OR-02 | `test_tc_or_02_yesno_invertido[0 -> Sí]` | Aprobado |
| TC-OR-02 | `test_tc_or_02_yesno_invertido[1 -> No]` | Aprobado |
| TC-OR-03 | `test_tc_or_03_datetime_zona_chile` | Aprobado |
| TC-OR-04 | `test_tc_or_04_pregunta_anidada_group` | Aprobado |
| TC-OR-05 | `test_tc_or_05_was_hidden_se_descarta` | Aprobado |
| TC-OR-06 | `test_tc_or_06_submitted_empty_con_dato_se_conserva` | Aprobado |
| TC-OR-07 | `test_tc_or_07_multiple_choice` | Aprobado |
| TC-OR-08 | `test_tc_or_08_sin_submissions` | Aprobado |
| TC-OR-09 | `test_tc_or_09_columnas_base_presentes` | Aprobado |
| TC-CN-01 | `test_tc_cn_01_detecta_ot_nueva` | Aprobado |
| TC-CN-02 | `test_tc_cn_02_ot_ya_procesada_se_omite` | Aprobado |
| TC-CN-03 | `test_tc_cn_03_sin_nuevas_retorna_false` | Aprobado |
| TC-CN-04 | `test_tc_cn_04_idempotencia_insercion` | Aprobado |
| TC-PE-01 | `test_tc_pe_01_inspeccion_se_enruta` | Aprobado |
| TC-PE-02 | `test_tc_pe_02_expansion_puntos` | Aprobado |
| TC-PE-03 | `test_tc_pe_03_mantencion_correctiva` | Aprobado |
| TC-PE-09 | `test_tc_pe_09_solicitud_de_obra` | Aprobado |
| TC-PE-10 | `test_tc_pe_10_tipo_simple_lt` | Aprobado |
| TC-PE-11 | `test_tc_pe_11_resolucion_proyecto` | Aprobado |
| TC-PE-13 | `test_tc_pe_13_prefijo_ot_y_tecnico` | Aprobado |
| TC-PE-15 | `test_tc_pe_15_orden_descendente_fecha` | Aprobado |
| TC-EX-01 | `test_tc_ex_01_insercion_incremental` | Aprobado |
| TC-EX-03 | `test_tc_ex_03_dataframe_vacio_no_escribe` | Aprobado |
| TC-EX-05 | `test_tc_ex_05_fallo_descarga` | Aprobado |

## 5. Hallazgos confirmados durante la ejecución

Las pruebas validan el comportamiento **real** del código, incluyendo particularidades que
se documentan en [../general_doc/07_processor_detalle.md](../general_doc/07_processor_detalle.md):

1. **`yesNo` invertido** (TC-OR-02): `selectedIndex == 0` produce `"Sí"`. Comportamiento
   confirmado y cubierto.
2. **`Tipo de trabajo` de reemplazos**: las ramas de reemplazo registran el subtipo
   (`E`/`I`), no el literal `R`; coherente con la documentación corregida. (Los casos
   TC-PE de reemplazo con subtipos pueden ampliarse con fixtures de columnas `R (E)`/`R (I)`).
3. **Aislamiento de la base**: confirmado que la deduplicación opera correctamente sobre una
   base temporal sin afectar producción.

## 6. Cobertura pendiente (no ejecutada en esta corrida)

Casos definidos en [03_casos_de_prueba.md](03_casos_de_prueba.md) que aún no tienen prueba
automatizada y requieren fixtures adicionales o entorno real:

- TC-PE-04 (MP con subtipos), TC-PE-05 (Instalación I/T/C), TC-PE-06/07 (Reemplazo y solo
  extracción), TC-PE-08 (CF), TC-PE-12 (punto "No encontrado"), TC-PE-14 (múltiples puntos),
  TC-PE-16 (límite de 9 puntos): requieren construir fixtures de columnas con la
  nomenclatura completa por subtipo.
- TC-API-* y TC-SP-*: requieren simular `requests` y MSAL (no incluidos en esta corrida por
  no afectar la lógica central de transformación).
- TC-INT-* y TC-SYS-*: integración y sistema; el segundo requiere credenciales y un destino
  SharePoint de prueba.

## 7. Reproducción

```bash
cd trabajos_terreno/qa
python3 -m pytest tests/ -v
```
