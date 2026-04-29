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



def main():
    sp = Sharepoint()
    
    while True:
        print('\nTipo de ejecución a realizar')
        print('----------------------------')
        print('(1) OTs específicas')
        print('(2) Salir')

        codigo = input('\nIndique un código: ')

        if codigo == '1':
        
            print('\nIndique las OTs a procesar (separadas por espacio): ')
            lista_ot = input('#: ').split(' ')
            try:
                ot = [int(i) for i in lista_ot]
            except ValueError:
                print("Entrada inválida. Por favor ingrese números.")
                continue
            
            try:
                # Obtiene la estructura del formulario y las submissions filtradas, luego las ordena
                ordered_responses = ordenar_respuestas(form_structure(CONNECTEAM_API_KEY), all_submission(CONNECTEAM_API_KEY))
            except Exception as e:
                # Si ocurre un error en la conexión a la API, lo muestra
                print(f"Ocurrio un problema con la conexión a la API-Connecteam: {e}")
                return
            
            sublista = ordered_responses[ordered_responses['#'].isin(ot)]

            data_terreno, data_inspeccion = process_entrys(sublista, CONNECTEAM_API_KEY) #sp al final del argumento

            print(tabulate.tabulate(data_inspeccion, headers='keys', tablefmt='grid'))

            try:
                # Envía los datos filtrados a SharePoint, actualizando los archivos correspondientes
                send_data(data_terreno, 'Terreno', 'OTS', sp)
                send_data(data_inspeccion, 'Inspección', 'Ronda', sp)


            except Exception as e:
                # Si ocurre un error al actualizar SharePoint, lo muestra
                print(f"Error al actualizar sharepoint: {e}")
        
        elif codigo == '2':
            break

if __name__ == "__main__":
    main()