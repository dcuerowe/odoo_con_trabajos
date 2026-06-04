"""Casos TC-EX — excel_manager.modify_excel_file / send_data.

Se usa un libro Excel local en memoria y un cliente SharePoint simulado; nunca se accede
al Terreno.xlsx de producción.
"""
import io

import openpyxl
from openpyxl.worksheet.table import Table
import pytest

import excel_manager


class FakeSharepoint:
    """Cliente SharePoint simulado: descarga desde memoria y captura la subida."""

    def __init__(self, data: bytes):
        self._data = data
        self.uploaded = None

    def download_file(self, url):
        return self._data

    def upload_file(self, url, content_stream, content_type=None, folder_name=""):
        content_stream.seek(0)
        self.uploaded = content_stream.read()
        return True


def _workbook_bytes():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Terreno"
    ws.append(["Col1", "Col2"])      # cabecera (fila 1)
    ws.append(["a", "b"])            # fila de datos existente (fila 2)
    ws.add_table(Table(displayName="OTS", ref="A1:B2"))
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def test_tc_ex_01_insercion_incremental():
    """TC-EX-01: las filas nuevas se anexan y la referencia de la tabla se expande."""
    sp = FakeSharepoint(_workbook_bytes())
    nuevas = [["c", "d"], ["e", "f"]]

    excel_manager.modify_excel_file(nuevas, "Terreno", "OTS", sp)

    assert sp.uploaded is not None
    wb = openpyxl.load_workbook(io.BytesIO(sp.uploaded))
    ws = wb["Terreno"]
    assert ws["A3"].value == "c"
    assert ws["A4"].value == "e"
    # fila previa intacta
    assert ws["A2"].value == "a"
    # referencia expandida de A1:B2 a A1:B4
    assert ws.tables["OTS"].ref == "A1:B4"


def test_tc_ex_03_dataframe_vacio_no_escribe():
    """TC-EX-03: send_data con DataFrame vacío no invoca la modificación."""
    import pandas as pd

    llamado = {"flag": False}

    def fake_modify(*args, **kwargs):
        llamado["flag"] = True

    original = excel_manager.modify_excel_file
    excel_manager.modify_excel_file = fake_modify
    try:
        excel_manager.send_data(pd.DataFrame(), "Terreno", "OTS", object())
    finally:
        excel_manager.modify_excel_file = original

    assert llamado["flag"] is False


def test_tc_ex_05_fallo_descarga(capsys):
    """TC-EX-05: si la descarga devuelve None, no se intenta subir."""
    class SPNulo:
        def download_file(self, url):
            return None
        def upload_file(self, *a, **k):
            raise AssertionError("no debe subirse si la descarga falló")

    excel_manager.modify_excel_file([["x", "y"]], "Terreno", "OTS", SPNulo())
    out = capsys.readouterr().out
    assert "No se pudo descargar" in out
