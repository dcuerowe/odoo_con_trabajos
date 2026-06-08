"""
Orquestación de informes PDF por trabajo.

`adjuntar_informes` toma el DataFrame `data_terreno` (salida de `process_entrys`),
genera un PDF por fila con `informe_pdf_profesional`, lo sube a SharePoint y agrega
una columna `Informe` con un hipervínculo clickeable al PDF. Devuelve el DataFrame
listo para `excel_manager.send_data` (sin la columna auxiliar `_fotos`).
"""

import re
import unicodedata
from datetime import date, datetime
from urllib.parse import quote

from config import INFORMES_BASE_URL
from informe_generator import informe_pdf_profesional


def _slug(texto):
    """Normaliza un texto para usarlo como nombre de archivo: sin acentos,
    sin caracteres conflictivos, espacios y separadores → '_'."""
    s = str(texto or "").strip()
    # Quitar acentos
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    # Quitar corchetes del proyecto y cualquier carácter no alfanumérico básico
    s = re.sub(r"[\[\]]", "", s)
    s = re.sub(r"[^0-9A-Za-z._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "x"


def _fecha_str(fecha):
    """Devuelve dd/mm/yyyy si es fecha; si no, el texto tal cual."""
    if isinstance(fecha, (date, datetime)):
        return fecha.strftime("%d/%m/%Y")
    return str(fecha) if fecha is not None else ""


def adjuntar_informes(df_terreno, sharepoint_client):
    """Genera+sube un PDF por fila y agrega la columna `Informe` (hipervínculo).

    Errores por fila se logean y no abortan el lote (la fila queda con `Informe`
    vacío). Elimina la columna auxiliar `_fotos` antes de devolver.
    """
    if df_terreno is None or df_terreno.empty:
        return df_terreno

    df = df_terreno.copy()
    if "_fotos" not in df.columns:
        df["_fotos"] = [[] for _ in range(len(df))]

    enlaces = []
    # Contador por (OT, Asset, Tipo de trabajo) para nombrar PDFs únicos cuando
    # un mismo punto tiene varios equipos del mismo tipo de trabajo.
    contador = {}

    for _, fila in df.iterrows():
        ot = fila.get("OT", "")
        asset = fila.get("Asset", "")
        tipo = fila.get("Tipo de trabajo", "")

        clave = (str(ot), str(asset), str(tipo))
        contador[clave] = contador.get(clave, 0) + 1
        n = contador[clave]

        nombre = f"{_slug(ot)}__{_slug(asset)}__{_slug(tipo)}__{n}.pdf"

        web_url = None
        try:
            pdf = informe_pdf_profesional(
                numero_visita=asset,
                ot=ot,
                tecnico=fila.get("Técnico"),
                proyecto=fila.get("Proyecto"),
                fecha=_fecha_str(fila.get("Fecha visita")),
                cliente=fila.get("Cliente"),
                tipo_equipo=fila.get("Equipo"),
                modelo=fila.get("Modelo"),
                serial=fila.get("N° de serie"),
                trabajo=tipo,
                alcance=fila.get("Alcance"),
                punto=asset,
                obs_especifica=fila.get("Observación"),
                obs_generales=fila.get("Resolución visita"),
                imagenes=fila.get("_fotos") or [],
                equipo=fila.get("Equipo"),
            )
            url_subida = f"{INFORMES_BASE_URL}/{quote(nombre, safe='')}:/content"
            web_url = sharepoint_client.upload_file(url_subida, pdf, content_type="pdf")
        except Exception as e:
            print(f"Error al generar/subir informe de {ot} · {asset} · {tipo}: {e}")

        if web_url:
            # Fórmula HYPERLINK: openpyxl la escribe como fórmula (link clickeable).
            enlaces.append(f'=HYPERLINK("{web_url}","Ver informe")')
        else:
            enlaces.append("")

    df["Informe"] = enlaces
    df = df.drop(columns=["_fotos"])
    return df
