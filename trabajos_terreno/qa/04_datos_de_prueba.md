# 04 — Datos de prueba

Este documento define fixtures reproducibles para las pruebas. Los ejemplos usan `pytest`
y `unittest.mock`; su adopción requiere añadir `pytest` a las dependencias de desarrollo.

## 1. Estructura mínima de formulario (`form_structure`)

```python
ESTRUCTURA = {
    "data": {
        "questions": [
            {"questionId": "q_visita", "title": "Tipo de visita realizada"},
            {"questionId": "q_contrato", "title": "Contrato"},
            {"questionId": "q_fecha", "title": "Fecha visita "},
            {
                "questionId": "g_punto1",
                "title": "Punto 1",
                "questions": [
                    {"questionId": "q_p1_punto", "title": "1.1 Punto de monitoreo"},
                    {"questionId": "q_p1_tipo", "title": "1.2 Tipo de trabajo a realizar"},
                    {"questionId": "q_p1_mc_modelo", "title": "1.2.1 MC | Modelo"},
                    {"questionId": "q_p1_mc_serie", "title": "1.2.1 MC | N° de serie"},
                    {"questionId": "q_p1_mc_activo", "title": "1.2.1 MC | Activo a intervenir"},
                    {"questionId": "q_p1_mc_op", "title": "1.2.1 MC | ¿Equipo operativo tras trabajos?"},
                    {"questionId": "q_p1_mc_obs", "title": "1.2.1 MC | Observación"},
                    {"questionId": "q_p1_res", "title": "1.3 Resolución de visita"},
                ],
            },
        ]
    }
}
```

## 2. Submission de trabajo (MC en un punto)

```python
SUBMISSION_MC = {
    "data": {
        "formSubmissions": [
            {
                "entryNum": 99001,
                "submittingUserId": 145,
                "submissionTimestamp": 1731412800,
                "answers": [
                    {"questionId": "q_visita", "questionType": "multipleChoice",
                     "selectedAnswers": [{"text": "Trabajo en terreno"}]},
                    {"questionId": "q_contrato", "questionType": "openEnded", "value": "C-001"},
                    {"questionId": "q_fecha", "questionType": "datetime", "timestamp": 1731412800},
                    {"questionId": "g_punto1", "questionType": "group", "answers": [
                        {"questionId": "q_p1_punto", "questionType": "openEnded",
                         "value": "Estación Norte [Proyecto XYZ]"},
                        {"questionId": "q_p1_tipo", "questionType": "multipleChoice",
                         "selectedAnswers": [{"text": "MC | Mantención Correctiva"}]},
                        {"questionId": "q_p1_mc_modelo", "questionType": "openEnded", "value": "Modelo-X"},
                        {"questionId": "q_p1_mc_serie", "questionType": "openEnded", "value": "SN-123"},
                        {"questionId": "q_p1_mc_activo", "questionType": "openEnded", "value": "Sensor de nivel"},
                        {"questionId": "q_p1_mc_op", "questionType": "yesNo", "selectedIndex": 0},
                        {"questionId": "q_p1_mc_obs", "questionType": "openEnded", "value": "Sin novedad"},
                        {"questionId": "q_p1_res", "questionType": "openEnded", "value": "Resuelto"},
                    ]},
                ],
            }
        ]
    }
}
```

> Nota: el `processor` requiere además las columnas globales de seguridad (`PT`, `DET`,
> `Cinco Pasos`, `Charla de 5 Minutos`, `Check List de Camioneta/ Somnolencia`, `AST`),
> `Causa visita`, `Nombre del Cliente` y `Calidad del Servicio`. Para pruebas unitarias de
> `process_entrys` conviene construir el DataFrame directamente con esas columnas (sección 4)
> en lugar de pasar por `ordenar_respuestas`.

## 3. Submission de inspección

```python
SUBMISSION_INSPECCION = {
    "data": {"formSubmissions": [{
        "entryNum": 99002,
        "submittingUserId": 145,
        "submissionTimestamp": 1731412800,
        "answers": [
            {"questionId": "q_visita", "questionType": "multipleChoice",
             "selectedAnswers": [{"text": "(R) Ronda diaria de Inspección"}]},
            # 'Puntos visitados' y 'Fotos ' según títulos reales del formulario
        ],
    }]}
}
```

## 4. DataFrame directo para `process_entrys` (recomendado para unitarias)

```python
import pandas as pd

def fila_mc():
    return {
        "#": 99001,
        "user": 145,
        "Tipo de visita realizada": "Trabajo en terreno",
        "Contrato": "C-001",
        "Causa visita": "Falla reportada",
        "Nombre del Cliente": "Cliente Demo",
        "Calidad del Servicio": "Buena",
        "Fecha visita ": "12-11-2025",
        "PT (Permiso de trabajo)": "Sí",
        "DET (Análisis de Riesgos)": "Sí",
        "Cinco Pasos para Trabajar Seguro": "Sí",
        "Charla de 5 Minutos": "Sí",
        "Check List de Camioneta/ Somnolencia": "Sí",
        "AST": "Sí",
        "1.1 Punto de monitoreo": "Estación Norte [Proyecto XYZ]",
        "1.2 Tipo de trabajo a realizar": "MC | Mantención Correctiva",
        "1.3 Resolución de visita": "Resuelto",
        "1.2.1 MC | Modelo": "Modelo-X",
        "1.2.1 MC | Activo a intervenir": "Sensor de nivel",
        "1.2.1 MC | N° de serie": "SN-123",
        "1.2.1 MC | ¿Equipo operativo tras trabajos?": "Sí",
        "1.2.1 MC | Observación": "Sin novedad",
    }

DF_MC = pd.DataFrame([fila_mc()])
```

## 5. SQLite temporal para `check_new_sub`

```python
import sqlite3

def crear_db_temporal(path):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE processed_entries (entry_id INTEGER PRIMARY KEY)")
    con.commit()
    con.close()
```

> `check_new_sub` resuelve la ruta de la base relativa a `data_processing.py`. Para apuntar
> a la base temporal, parchear `data_processing.__file__` o, preferentemente, refactorizar
> la función para aceptar la ruta como parámetro (mejora pendiente, ver
> [05_checklist_release.md](05_checklist_release.md)).

## 6. Ejemplo de prueba (pytest)

```python
from unittest.mock import patch
import processor

@patch("processor.user", return_value="Diego Marchant")
def test_mc_genera_un_registro(mock_user):
    terreno, inspeccion = processor.process_entrys(DF_MC, "API_KEY_FALSA")
    assert len(terreno) == 1
    fila = terreno.iloc[0]
    assert fila["OT"] == "III-99001"
    assert fila["Tipo de trabajo"] == "MC"
    assert fila["Proyecto"] == "Proyecto XYZ"
    assert fila["Asset"] == "Estación Norte"
    assert fila["Alcance"] is None
    assert inspeccion.empty
```

## 7. Excel de prueba

Mantener una copia de `Terreno.xlsx` con las hojas `Terreno` (tabla `OTS`) e `Inspección`
(tabla `Ronda`) en una ruta de prueba. Para validar `modify_excel_file` sin red, sustituir
`download_file` por la lectura de ese archivo y `upload_file` por una escritura a disco, y
luego reabrir con `openpyxl` para verificar filas y `tabla.ref`.
