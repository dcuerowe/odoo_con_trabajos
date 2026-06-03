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

            if sublista.empty:
                print("No se encontraron las OTs indicadas en las submissions disponibles.")
                continue

            # Segundo filtro: dentro de cada OT, elegir qué puntos gestionar.
            # Los puntos se identifican por el prefijo numérico de las columnas
            # (mismo criterio que process_entrys: col[0]), p.ej. "1.1 Punto de monitoreo" -> punto "1".
            filas_filtradas = []
            for _, fila in sublista.iterrows():
                fila_limpia = fila.dropna()
                puntos = sorted({c[0] for c in fila_limpia.index if c and c[0].isdigit()})

                if not puntos:
                    filas_filtradas.append(fila)
                    continue

                ot_num = fila_limpia['#']
                print(f"\nOT {ot_num} — puntos disponibles:")
                for p in puntos:
                    col_nombre = f'{p}.1 Punto de monitoreo'
                    nombre = fila_limpia[col_nombre] if col_nombre in fila_limpia.index else '(sin nombre)'
                    print(f'  ({p}) {nombre}')

                seleccion = input(f'Puntos a gestionar de la OT {ot_num} (separados por espacio) [Enter = todos]: ').split()

                if seleccion:
                    desconocidos = [p for p in seleccion if p not in puntos]
                    if desconocidos:
                        print(f"  Aviso: se ignoran puntos no presentes en la OT: {' '.join(desconocidos)}")
                    puntos_keep = {p for p in seleccion if p in puntos}
                    if not puntos_keep:
                        print(f"  No quedaron puntos válidos para la OT {ot_num}; se omite.")
                        continue
                    # Conservamos columnas globales (sin prefijo numérico) y las de los puntos elegidos
                    columnas_keep = [c for c in fila.index
                                     if not (c and c[0].isdigit()) or c[0] in puntos_keep]
                    fila = fila[columnas_keep]

                filas_filtradas.append(fila)

            if not filas_filtradas:
                print("No quedaron puntos por gestionar tras el filtro.")
                continue

            sublista = pd.DataFrame(filas_filtradas)

            data_terreno, data_inspeccion = process_entrys(sublista, CONNECTEAM_API_KEY) #sp al final del argumento

            print(f"\nTrabajos en terreno (data_terreno): {len(data_terreno)} fila(s)")
            if not data_terreno.empty:
                print(tabulate.tabulate(data_terreno, headers='keys', tablefmt='grid'))

            print(f"\nRondas de inspección (data_inspeccion): {len(data_inspeccion)} fila(s)")
            if not data_inspeccion.empty:
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