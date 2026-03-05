import time
import schedule
import pandas as pd
import tabulate
import sqlite3
import traceback
import os
from config import (
    SHAREPOINT_USER, SHAREPOINT_PASSWORD, SHAREPOINT_SITE, SHAREPOINT_NAME_SITE, SHAREPOINT_DOC_LIBRARY,
    CONNECTEAM_API_KEY
)
from sharepoint_client import Sharepoint
from connecteam_api import all_submission, filter_submissions, form_structure
from data_processing import ordenar_respuestas, check_new_sub
from processor import process_entrys
from excel_manager import send_data


def job():
    print('\n-> Detección automática de OTs en Connecteam')
    
    # Initialize Clients
    sp = Sharepoint()

    try:
        # Obtiene la estructura del formulario y las submissions filtradas, luego las ordena
        ordered_responses = ordenar_respuestas(form_structure(CONNECTEAM_API_KEY), all_submission(CONNECTEAM_API_KEY))
    except Exception as e:
        # Si ocurre un error en la conexión a la API, lo muestra
        print(f"Ocurrio un problema con la conexión a la API-Connecteam: {e}")
        return

    print(f"\n[{time.ctime()}] Buscando nuevas entradas...")
    try:
        # Busca nuevas OTs que no hayan sido procesadas previamente
        nuevas_entradas = check_new_sub(ordered_responses)

        if isinstance(nuevas_entradas, pd.DataFrame) and not nuevas_entradas.empty:

            print(f"Se encontraron {len(nuevas_entradas)} nuevas entradas. Procesando...")

            # Procesa las nuevas entradas encontradas
            data = process_entrys(nuevas_entradas, CONNECTEAM_API_KEY) #sp al final del argumento

            print(tabulate.tabulate(data, headers='keys', tablefmt='grid'))

            try:
                # Envía los datos filtrados a SharePoint, actualizando los archivos correspondientes
                send_data(data, 'Terreno', 'OTS', sp)


            except Exception as e:
                # Si ocurre un error al actualizar SharePoint, lo muestra
                print(f"Error al actualizar sharepoint: {e}")

    except Exception as e:
        # Si ocurre un error durante la ejecución de la tarea, lo muestra
        print(f"Ocurrió un error durante la ejecución de la tarea: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    job()
