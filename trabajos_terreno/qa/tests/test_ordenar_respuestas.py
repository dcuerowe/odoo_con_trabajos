"""Casos TC-OR — data_processing.ordenar_respuestas."""
import datetime as dt

import pandas as pd
import pytest

from data_processing import ordenar_respuestas


def test_tc_or_01_open_ended(estructura_basica, make_submission):
    """TC-OR-01: openEnded se extrae como value."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_open", "questionType": "openEnded", "value": "C-001"},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "Contrato"] == "C-001"


@pytest.mark.parametrize("idx,esperado", [(0, "Sí"), (1, "No")])
def test_tc_or_02_yesno_invertido(estructura_basica, make_submission, idx, esperado):
    """TC-OR-02: selectedIndex 0 -> 'Sí', 1 -> 'No'."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_yesno", "questionType": "yesNo", "selectedIndex": idx},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "Operativo"] == esperado


def test_tc_or_03_datetime_zona_chile(estructura_basica, make_submission):
    """TC-OR-03: datetime devuelve un date en America/Santiago."""
    # 2025-11-12 12:00:00 UTC
    ts = int(dt.datetime(2025, 11, 12, 12, 0, tzinfo=dt.timezone.utc).timestamp())
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_fecha", "questionType": "datetime", "timestamp": ts},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    valor = df.loc[0, "Fecha visita "]
    assert isinstance(valor, dt.date)
    # En noviembre Chile está en UTC-3 -> mismo día 12
    assert valor == dt.date(2025, 11, 12)


def test_tc_or_04_pregunta_anidada_group(estructura_basica, make_submission):
    """TC-OR-04: preguntas dentro de un bloque group se mapean por título."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "g1", "questionType": "group", "answers": [
            {"questionId": "q_anidada", "questionType": "openEnded", "value": "Valor anidado"},
        ]},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "Punto anidado"] == "Valor anidado"


def test_tc_or_05_was_hidden_se_descarta(estructura_basica, make_submission):
    """TC-OR-05: wasHidden=True descarta la respuesta."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_open", "questionType": "openEnded", "value": "oculto", "wasHidden": True},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert "Contrato" not in df.columns


def test_tc_or_06_submitted_empty_con_dato_se_conserva(estructura_basica, make_submission):
    """TC-OR-06: wasSubmittedEmpty=True con value real se conserva."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_open", "questionType": "openEnded", "value": "dato real",
         "wasSubmittedEmpty": True},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "Contrato"] == "dato real"


def test_tc_or_07_multiple_choice(estructura_basica, make_submission):
    """TC-OR-07: multipleChoice une textos por ', '."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_mc", "questionType": "multipleChoice",
         "selectedAnswers": [{"text": "A"}, {"text": "B"}]},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "Multi"] == "A, B"


def test_tc_or_08_sin_submissions(estructura_basica):
    """TC-OR-08: sin submissions devuelve DataFrame vacío."""
    df = ordenar_respuestas(estructura_basica, {"data": {"formSubmissions": []}})
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_tc_or_09_columnas_base_presentes(estructura_basica, make_submission):
    """TC-OR-09 (complemento): columnas base #, user, fecha_envio siempre presentes."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_open", "questionType": "openEnded", "value": "x"},
    ], entry=555, user=145)]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "#"] == 555
    assert df.loc[0, "user"] == 145
    assert df.loc[0, "fecha_envio"] != ""
