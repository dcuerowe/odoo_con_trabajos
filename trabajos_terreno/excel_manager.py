import io
from datetime import date, datetime
import openpyxl
from openpyxl.utils.cell import coordinate_to_tuple
from openpyxl.utils import get_column_letter
from config import EXCEL_URL

def modify_excel_file(resumen, sheet_name, table_name, sharepoint_client):
    # Descarga el archivo Excel desde SharePoint
    excel = sharepoint_client.download_file(EXCEL_URL)
    if excel:
        try:
            # Convierte los bytes descargados en un objeto BytesIO para manipulación en memoria
            excel_file = io.BytesIO(excel)
            # Carga el archivo Excel en openpyxl
            wl = openpyxl.load_workbook(excel_file)
            # Selecciona la hoja de trabajo especificada
            wh = wl[sheet_name]

            # Obtiene la tabla de la hoja por su nombre
            tabla = wh.tables[table_name]
            # Obtiene la referencia actual de la tabla (ejemplo: 'A1:H10')
            ref_actual = tabla.ref
            # Extrae las coordenadas inicial y final de la tabla
            referencia_inicial = ref_actual.split(':')[0]
            coordenada_final = ref_actual.split(':')[-1]
            fila_header, col_inicio = coordinate_to_tuple(referencia_inicial)
            fila_final_actual, columna_final_num = coordinate_to_tuple(coordenada_final)

            # Nuevos registros se insertan en la primera fila de datos (debajo del header)
            # para que los más recientes queden arriba.
            fila_inicio_nuevos_datos = fila_header + 1
            n_nuevas = len(resumen)

            # Hace espacio desplazando hacia abajo los datos existentes
            wh.insert_rows(idx=fila_inicio_nuevos_datos, amount=n_nuevas)

            # Escribe los nuevos datos en las filas recién insertadas
            for i, fila_nueva in enumerate(resumen):
                for j, valor in enumerate(fila_nueva):
                    cell = wh.cell(row=fila_inicio_nuevos_datos + i, column=col_inicio + j, value=valor)
                    if isinstance(valor, (date, datetime)):
                        cell.number_format = 'DD/MM/YY'

            # Actualiza la referencia de la tabla para incluir las nuevas filas
            fila_final_nueva = fila_final_actual + n_nuevas
            columna_final_letra = get_column_letter(columna_final_num)
            nueva_referencia = f'{referencia_inicial}:{columna_final_letra}{fila_final_nueva}'
            tabla.ref = nueva_referencia
            # --- Fin del código de openpyxl ---

            # Guarda el archivo modificado en un nuevo stream de bytes
            excel_stream_out = io.BytesIO()
            wl.save(excel_stream_out)
            excel_stream_out.seek(0)  # Mueve el cursor al inicio del stream
            
            # Sube el archivo modificado de vuelta a SharePoint
            success = sharepoint_client.upload_file(EXCEL_URL, excel_stream_out)

        except Exception as e:
            print(f"Error al procesar el archivo Excel: {e}")
            
    else:
        print("No se pudo descargar el archivo.")

def send_data(df, sheet, table, sharepoint_client):
    manual = df.values.tolist()
    if manual != []:
        modify_excel_file(manual, sheet, table, sharepoint_client)
