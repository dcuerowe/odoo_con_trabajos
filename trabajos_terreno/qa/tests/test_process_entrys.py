"""Casos TC-PE — processor.process_entrys.

Se parchea processor.user para evitar llamadas de red a la API de Connecteam.
"""
import pandas as pd
import pytest

import processor


@pytest.fixture(autouse=True)
def mock_user(monkeypatch):
    monkeypatch.setattr(processor, "user", lambda api, uid: "Diego Marchant")


def test_tc_pe_01_inspeccion_se_enruta(fila_inspeccion, fila_mc):
    """TC-PE-01: una ronda de inspección va a df_inspeccion, no a df_terreno."""
    df = pd.DataFrame([fila_inspeccion, fila_mc])
    terreno, inspeccion = processor.process_entrys(df, "API")
    assert not inspeccion.empty
    assert set(terreno["Tipo de trabajo"]) == {"MC"}


def test_tc_pe_02_expansion_puntos(fila_inspeccion):
    """TC-PE-02: 'Puntos visitados' separados por coma generan una fila por punto."""
    df = pd.DataFrame([fila_inspeccion])
    _, inspeccion = processor.process_entrys(df, "API")
    assert len(inspeccion) == 3
    assert set(inspeccion["Puntos visitados"]) == {"Punto A", "Punto B", "Punto C"}
    assert "Fotos " not in inspeccion.columns


def test_tc_pe_03_mantencion_correctiva(fila_mc):
    """TC-PE-03: MC genera un registro con Alcance None y campos de equipo poblados."""
    df = pd.DataFrame([fila_mc])
    terreno, _ = processor.process_entrys(df, "API")
    assert len(terreno) == 1
    fila = terreno.iloc[0]
    assert fila["Tipo de trabajo"] == "MC"
    assert fila["Modelo"] == "Modelo-X"
    assert fila["N° serie"] == "SN-123"
    assert fila["Equipo"] == "Sensor de nivel"
    assert fila["Alcance"] is None


def test_tc_pe_09_solicitud_de_obra(fila_so):
    """TC-PE-09: SO registra Alcance y deja Equipo/Modelo/Serie en None."""
    df = pd.DataFrame([fila_so])
    terreno, _ = processor.process_entrys(df, "API")
    fila = terreno.iloc[0]
    assert fila["Tipo de trabajo"] == "SO"
    assert fila["Alcance"] == "Obra civil"
    assert fila["Equipo"] is None
    assert fila["Modelo"] is None
    assert fila["N° serie"] is None


def test_tc_pe_10_tipo_simple_lt(fila_lt):
    """TC-PE-10: LT genera un registro sin datos de equipo."""
    df = pd.DataFrame([fila_lt])
    terreno, _ = processor.process_entrys(df, "API")
    fila = terreno.iloc[0]
    assert fila["Tipo de trabajo"] == "LT"
    assert fila["Equipo"] is None
    assert fila["Alcance"] is None
    assert fila["Observación"] is None


def test_tc_pe_11_resolucion_proyecto(fila_mc):
    """TC-PE-11: el proyecto se extrae de [...] y se limpia del nombre del punto."""
    df = pd.DataFrame([fila_mc])
    terreno, _ = processor.process_entrys(df, "API")
    fila = terreno.iloc[0]
    assert fila["Proyecto"] == "Proyecto XYZ"
    assert fila["Asset"] == "Estación Norte"


def test_tc_pe_13_prefijo_ot_y_tecnico(fila_mc):
    """TC-PE-13: OT lleva prefijo III- y el técnico se resuelve vía API (mock)."""
    df = pd.DataFrame([fila_mc])
    terreno, _ = processor.process_entrys(df, "API")
    fila = terreno.iloc[0]
    assert fila["OT"] == "III-99001"
    assert fila["Técnico"] == "Diego Marchant"


def test_tc_pe_15_orden_descendente_fecha(fila_mc):
    """TC-PE-15: el resultado de terreno se ordena por fecha descendente."""
    f1 = dict(fila_mc); f1["#"] = 1; f1["Fecha visita "] = "01-11-2025"
    f2 = dict(fila_mc); f2["#"] = 2; f2["Fecha visita "] = "20-11-2025"
    df = pd.DataFrame([f1, f2])
    terreno, _ = processor.process_entrys(df, "API")
    fechas = list(terreno["Fecha visita"])
    assert fechas == sorted(fechas, reverse=True)
