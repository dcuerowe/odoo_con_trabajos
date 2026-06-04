"""Configuración común de las pruebas QA.

Inserta el directorio de la aplicación (`trabajos_terreno/`) en `sys.path` para que los
módulos con imports planos (`from config import ...`) sean importables, y expone fixtures
reutilizables de datos de prueba.
"""
import sys
from pathlib import Path

# tests -> qa -> trabajos_terreno
APP_DIR = Path(__file__).resolve().parents[2]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import pandas as pd
import pytest


# --------------------------------------------------------------------------- #
# Fixtures de submissions crudas (formato API Connecteam) para ordenar_respuestas
# --------------------------------------------------------------------------- #
@pytest.fixture
def estructura_basica():
    return {
        "data": {
            "questions": [
                {"questionId": "q_open", "title": "Contrato"},
                {"questionId": "q_yesno", "title": "Operativo"},
                {"questionId": "q_fecha", "title": "Fecha visita "},
                {"questionId": "q_mc", "title": "Multi"},
                {
                    "questionId": "g1",
                    "title": "Grupo 1",
                    "questions": [
                        {"questionId": "q_anidada", "title": "Punto anidado"},
                    ],
                },
            ]
        }
    }


def _submission(answers, entry=1000, user=145, ts=1731412800):
    return {
        "entryNum": entry,
        "submittingUserId": user,
        "submissionTimestamp": ts,
        "answers": answers,
    }


@pytest.fixture
def make_submission():
    return _submission


# --------------------------------------------------------------------------- #
# Fixtures de filas para process_entrys (DataFrame ya aplanado)
# --------------------------------------------------------------------------- #
_GLOBALES_SEGURIDAD = {
    "Causa visita": "Falla reportada",
    "Nombre del Cliente": "Cliente Demo",
    "Calidad del Servicio": "Buena",
    "PT (Permiso de trabajo)": "Sí",
    "DET (Análisis de Riesgos)": "Sí",
    "Cinco Pasos para Trabajar Seguro": "Sí",
    "Charla de 5 Minutos": "Sí",
    "Check List de Camioneta/ Somnolencia": "Sí",
    "AST": "Sí",
}


def _fila_base(num):
    fila = {
        "#": num,
        "user": 145,
        "Tipo de visita realizada": "Trabajo en terreno",
        "Contrato": "C-001",
        "Fecha visita ": "12-11-2025",
    }
    fila.update(_GLOBALES_SEGURIDAD)
    return fila


@pytest.fixture
def fila_mc():
    fila = _fila_base(99001)
    fila.update({
        "1.1 Punto de monitoreo": "Estación Norte [Proyecto XYZ]",
        "1.2 Tipo de trabajo a realizar": "MC | Mantención Correctiva",
        "1.3 Resolución de visita": "Resuelto",
        "1.2.1 MC | Modelo": "Modelo-X",
        "1.2.1 MC | Activo a intervenir": "Sensor de nivel",
        "1.2.1 MC | N° de serie": "SN-123",
        "1.2.1 MC | ¿Equipo operativo tras trabajos?": "Sí",
        "1.2.1 MC | Observación": "Sin novedad",
    })
    return fila


@pytest.fixture
def fila_so():
    fila = _fila_base(99003)
    fila.update({
        "1.1 Punto de monitoreo": "Estación Sur [Proyecto ABC]",
        "1.2 Tipo de trabajo a realizar": "SO | Solicitud de Obra",
        "1.3 Resolución de visita": "Pendiente",
        "1.2.1 SO | Tipo de solicitud": "Obra civil",
        "1.2.1 SO | Observación": "Requiere base de hormigón",
    })
    return fila


@pytest.fixture
def fila_lt():
    fila = _fila_base(99004)
    fila.update({
        "1.1 Punto de monitoreo": "Estación Este [Proyecto DEF]",
        "1.2 Tipo de trabajo a realizar": "LT | Levantamiento",
        "1.3 Resolución de visita": "Resuelto",
    })
    return fila


@pytest.fixture
def fila_inspeccion():
    return {
        "#": 99002,
        "user": 145,
        "Tipo de visita realizada": "(R) Ronda diaria de Inspección",
        "Fecha visita ": "12-11-2025",
        "Puntos visitados": "Punto A, Punto B, Punto C",
        "Fotos ": "url1, url2",
    }
