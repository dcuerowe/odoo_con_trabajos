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


def test_tc_or_05_was_hidden_sin_dato_se_descarta(estructura_basica, make_submission):
    """TC-OR-05: wasHidden=True sin dato real se descarta."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_open", "questionType": "openEnded", "value": "", "wasHidden": True},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert "Contrato" not in df.columns


def test_tc_or_10_was_hidden_con_dato_se_conserva(estructura_basica, make_submission):
    """TC-OR-10 (regresión OT 255): wasHidden=True con dato real se CONSERVA.

    Caso: una submission editada en Connecteam para cambiar la rama condicional
    (p.ej. I -> CF) devuelve las casillas rellenadas con wasHidden=True. El valor
    real no debe descartarse.
    """
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_open", "questionType": "openEnded",
         "value": "Datalogger simex multicon", "wasHidden": True, "wasSubmittedEmpty": True},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "Contrato"] == "Datalogger simex multicon"


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


# --------------------------------------------------------------------------- #
# Sección "Gestión de residuos": títulos que colisionan entre grupos
# --------------------------------------------------------------------------- #
_ESTRUCTURA_RESIDUOS = {
    "data": {
        "questions": [
            {"questionId": "q_hubo", "title": "¿Hubo residuos?"},
            {
                "questionId": "g_plast",
                "title": "Plásticos y electrónicos",
                "questions": [
                    {"questionId": "p_det", "title": "Detalle de residuo"},
                    {"questionId": "p_cant", "title": "Cantidad"},
                ],
            },
            {
                "questionId": "g_pelig",
                "title": "Residuos peligrosos",
                "questions": [
                    {"questionId": "x_tipo", "title": "Indicar tipo de residuo"},
                    {"questionId": "x_cant", "title": "Cantidad"},
                ],
            },
            # 'Detalle de residuo' también se repite en el formulario real
            # (Plásticos y electrónicos + Desechos), así que debe prefijarse.
            {
                "questionId": "g_desech",
                "title": "Desechos",
                "questions": [
                    {"questionId": "d_det", "title": "Detalle de residuo"},
                    {"questionId": "d_cant", "title": "Cantidad"},
                ],
            },
        ]
    }
}


def test_tc_or_10_titulos_duplicados_se_prefijan_con_el_grupo(make_submission):
    """TC-OR-10: 'Cantidad' se repite en dos grupos; antes el segundo sobreescribía
    al primero. Ahora cada uno queda en su propia columna con el prefijo del grupo."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_hubo", "questionType": "yesNo", "selectedIndex": 0},
        {"questionId": "g_plast", "questionType": "group", "answers": [
            {"questionId": "p_det", "questionType": "openEnded", "value": "Cables UTP"},
            {"questionId": "p_cant", "questionType": "openEnded", "value": "Bolsa chica"},
        ]},
        {"questionId": "g_pelig", "questionType": "group", "answers": [
            {"questionId": "x_tipo", "questionType": "openEnded", "value": "Batería"},
            {"questionId": "x_cant", "questionType": "openEnded", "value": "1 unidad"},
        ]},
    ])]}}
    df = ordenar_respuestas(_ESTRUCTURA_RESIDUOS, resp)

    assert df.loc[0, "Plásticos y electrónicos | Cantidad"] == "Bolsa chica"
    assert df.loc[0, "Residuos peligrosos | Cantidad"] == "1 unidad"
    assert df.loc[0, "Plásticos y electrónicos | Detalle de residuo"] == "Cables UTP"
    # 'Indicar tipo de residuo' es único en el formulario: conserva su nombre.
    assert df.loc[0, "Indicar tipo de residuo"] == "Batería"
    assert df.loc[0, "¿Hubo residuos?"] == "Sí"
    assert "Cantidad" not in df.columns
    assert "Detalle de residuo" not in df.columns


def test_tc_or_11_titulo_unico_en_grupo_no_se_prefija(estructura_basica, make_submission):
    """TC-OR-11: un hijo de grupo con título único mantiene su nombre de columna
    (garantiza que los títulos '1.2.1 MC | Modelo' del formulario no cambien)."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "g1", "questionType": "group", "answers": [
            {"questionId": "q_anidada", "questionType": "openEnded", "value": "P-1"},
        ]},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert df.loc[0, "Punto anidado"] == "P-1"


def test_tc_or_12_group_anidado_no_se_pierde(make_submission):
    """TC-OR-12: un group dentro de otro group se recorre en profundidad; antes
    caía en el caso por defecto de extraer_valor y se descartaba en silencio."""
    estructura = {
        "data": {
            "questions": [
                {
                    "questionId": "g_ext",
                    "title": "Externo",
                    "questions": [
                        {
                            "questionId": "g_int",
                            "title": "Interno",
                            "questions": [
                                {"questionId": "q_hoja", "title": "Dato profundo"},
                            ],
                        },
                    ],
                },
            ]
        }
    }
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "g_ext", "questionType": "group", "answers": [
            {"questionId": "g_int", "questionType": "group", "answers": [
                {"questionId": "q_hoja", "questionType": "openEnded", "value": "v"},
            ]},
        ]},
    ])]}}
    df = ordenar_respuestas(estructura, resp)
    assert df.loc[0, "Dato profundo"] == "v"


def test_tc_or_13_tipo_desconocido_se_descarta_con_aviso(
    estructura_basica, make_submission, capsys
):
    """TC-OR-13: un questionType no soportado se descarta, pero deja aviso en
    consola para que un cambio de formulario no pase inadvertido."""
    resp = {"data": {"formSubmissions": [make_submission([
        {"questionId": "q_open", "questionType": "dropdown", "value": "x"},
    ])]}}
    df = ordenar_respuestas(estructura_basica, resp)
    assert "Contrato" not in df.columns
    assert "questionType no soportado" in capsys.readouterr().out
