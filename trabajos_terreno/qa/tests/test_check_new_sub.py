"""Casos TC-CN — data_processing.check_new_sub.

Aislamiento: se parchea sqlite3.connect del módulo para redirigir SIEMPRE a una base
temporal, garantizando que la base de producción form_entries.db no se toque.
"""
import sqlite3

import pandas as pd
import pytest

import data_processing
from data_processing import check_new_sub


@pytest.fixture
def db_temporal(tmp_path, monkeypatch):
    """Crea una base temporal con el esquema real y redirige sqlite3.connect."""
    db_path = tmp_path / "form_entries_test.db"
    real_connect = sqlite3.connect  # referencia real antes de parchear
    con = real_connect(db_path)
    con.execute("CREATE TABLE processed_entries (entry_id INTEGER PRIMARY KEY)")
    con.commit()
    con.close()

    def fake_connect(*args, **kwargs):
        return real_connect(db_path)

    monkeypatch.setattr(data_processing.sqlite3, "connect", fake_connect)
    return db_path


def _df(ids):
    return pd.DataFrame({"#": ids})


def _ids_en_db(db_path):
    con = sqlite3.connect(db_path)
    filas = {r[0] for r in con.execute("SELECT entry_id FROM processed_entries").fetchall()}
    con.close()
    return filas


def test_tc_cn_01_detecta_ot_nueva(db_temporal):
    """TC-CN-01: una OT nueva se devuelve y su ID queda insertado."""
    resultado = check_new_sub(_df([101, 102]))
    assert isinstance(resultado, pd.DataFrame)
    assert set(resultado["#"]) == {101, 102}
    assert _ids_en_db(db_temporal) == {101, 102}


def test_tc_cn_02_ot_ya_procesada_se_omite(db_temporal):
    """TC-CN-02: una OT ya presente no se devuelve como nueva."""
    check_new_sub(_df([101]))  # inserta 101
    resultado = check_new_sub(_df([101, 103]))
    assert isinstance(resultado, pd.DataFrame)
    assert set(resultado["#"]) == {103}


def test_tc_cn_03_sin_nuevas_retorna_false(db_temporal):
    """TC-CN-03: si no hay OT nuevas, retorna False."""
    check_new_sub(_df([200]))
    resultado = check_new_sub(_df([200]))
    assert resultado is False


def test_tc_cn_04_idempotencia_insercion(db_temporal):
    """TC-CN-04: reejecutar no duplica IDs ni vuelve a marcar como nueva."""
    check_new_sub(_df([300]))
    check_new_sub(_df([300]))
    assert _ids_en_db(db_temporal) == {300}
