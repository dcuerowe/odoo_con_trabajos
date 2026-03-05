import pandas as pd
import sqlite3
import traceback
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import re

def ordenar_respuestas(estructura, respuestas):
   # --- 1. Mapeo Recursivo de IDs de preguntas a Títulos ---
    # Es crucial porque las preguntas ahora están dentro de 'group' -> 'questions'
    questions = estructura.get('data', {}).get('questions', [])
    question_id_to_title = {}

    def map_questions(q_list):
        for q in q_list:
            question_id_to_title[q['questionId']] = q['title']
            # Si es un grupo, mirar adentro recursivamente
            if 'questions' in q:
                map_questions(q['questions'])
    
    map_questions(questions)

    # --- 2. Función Auxiliar para extraer valores (La misma lógica robusta) ---
    def extraer_valor(answer_obj):
        # Si no se respondió o está oculta, retornamos None
        if answer_obj.get('wasSubmittedEmpty', False) or answer_obj.get('wasHidden', False):
            return None

        q_type = answer_obj.get('questionType', 'unknown')

        if q_type == 'openEnded':
            return answer_obj.get('value', '')
        elif q_type == 'multipleChoice':
            selected = [opt['text'] for opt in answer_obj.get('selectedAnswers', [])]
            return ', '.join(selected) if selected else ''
        elif q_type == 'yesNo':
             # Ajuste para que '0' sea 'Sí' y '1' sea 'No' según tu historial, o el texto si existe
             idx = answer_obj.get('selectedIndex')
             if idx == 0: return "Sí"
             if idx == 1: return "No"
             return str(idx)
        elif q_type == 'datetime':
            ts = answer_obj.get('timestamp')
            if ts:
                try:
                    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
                    dt_chile = dt_utc.astimezone(ZoneInfo("America/Santiago"))
                    # Devuelve fecha y hora si existen, o solo fecha
                    return dt_chile.strftime("%d-%m-%Y")
                except:
                    return 'Error Fecha'
            return ''
        elif q_type == 'image':
            # Extraer URLs si existen
            imgs = answer_obj.get('images', [])
            return [img.get('url', '') for img in imgs] if imgs else []
        elif q_type == 'signature':
            return "Firma Capturada" if answer_obj.get('images') else "Sin Firma"
        elif q_type == 'rating':
            return answer_obj.get('ratingValue', '')
        elif q_type == 'description':
            return None 
        
        return None # Caso por defecto

    # --- 3. Procesamiento de Submissions ---
    lista_registros = []
    submissions = respuestas.get('data', {}).get('formSubmissions', [])

    for submission in submissions:
        # Datos base de la submission
        ts_envio = submission.get('submissionTimestamp')
        fecha_envio_str = ""
        if ts_envio:
             dt_envio = datetime.fromtimestamp(ts_envio, tz=timezone.utc).astimezone(ZoneInfo("America/Santiago"))
             fecha_envio_str = dt_envio.strftime("%d-%m-%Y")

        fila_datos = {
            '#': submission.get('entryNum'),
            'user': submission.get('submittingUserId'),
            'fecha_envio': fecha_envio_str
        }

        # Iterar sobre las respuestas principales
        for answer in submission.get('answers', []):
            q_type = answer.get('questionType')
            q_id = answer.get('questionId')
            
            # --- CASO GROUP (NUEVO) ---
            # El tipo 'group' contiene una lista 'answers' directa, no 'groupAnswers'
            if q_type == 'group' and 'answers' in answer:
                # Iteramos sobre las respuestas DENTRO del grupo
                for ans_anidada in answer['answers']:
                    sub_id = ans_anidada.get('questionId')
                    # Buscamos el título usando el ID (que ya mapeamos recursivamente)
                    titulo = question_id_to_title.get(sub_id, f"Pregunta {sub_id}")
                    
                    val = extraer_valor(ans_anidada)
                    if val is not None:
                        fila_datos[titulo] = val
            
            # --- CASO PREGUNTA NORMAL ---
            else:
                titulo = question_id_to_title.get(q_id, f"Pregunta {q_id}")
                val = extraer_valor(answer)
                if val is not None:
                    fila_datos[titulo] = val

        lista_registros.append(fila_datos)

    # --- 4. Generación del DataFrame ---
    if not lista_registros:
        return pd.DataFrame()

    df_final = pd.DataFrame(lista_registros)
    return df_final


def check_new_sub(ordered_responses):    
    """
    Procesa una lista de respuestas ordenadas para identificar y registrar nuevas OTs (órdenes de trabajo) en una base de datos SQLite.
    """

    # if not ordered_responses:
    #    print("No se encontraron nuevas OTs para procesar.") 
    #    return
    
    # SE CAMBIA LA FORMA DE GENERAR EL CONJUNTO DE INTERES
    ots = set(ordered_responses["#"])
    ots_id = {int(i) for i in ots}

    # 1. Obtener la ruta absoluta del directorio donde está ESTE script (main.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Construir la ruta completa a la base de datos
    db_path = os.path.join(BASE_DIR, 'form_entries.db')
    
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()

            # --- BLOQUE DE DEBUG: LISTAR TABLAS ---
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()
            
            # ---------------------------------------

            # Creamos placeholders (?,?,?) para una consulta segura
            if ots_id:
                placeholders = ','.join(['?'] * len(list(ots_id)))
                query = f"SELECT entry_id FROM processed_entries WHERE entry_id IN ({placeholders})"
                cursor.execute(query, tuple(ots_id))
                # El resultado es una lista de tuplas (e.g., [(101,), (102,)]), las convertimos a un set.
                processed_ids = {row[0] for row in cursor.fetchall()}
            else:
                processed_ids = set()
    

            # Comparar para encontrar solo lo nuevo
            new_ids = ots_id - processed_ids
            if not new_ids:
                print("No hay nuevas OTs para procesar.")
                return False

            # new_entries = [i for i in ordered_responses if i["#"][0] in new_ids]
            
            # SE CAMBIA LA FORMA DE FILTRADO
            new_entries = ordered_responses[ordered_responses["#"].isin(new_ids)]

            # Registrar en la base de datos el ID de las nuevas OT encontradas
            for entry in new_ids:
                cursor.execute("INSERT OR IGNORE INTO processed_entries (entry_id) VALUES (?)", ((entry),))
                print(f"ID {entry} guardado en la base de datos.")
            
            return new_entries
    
    except sqlite3.Error as e:
        print(f'Error en la base de datos: {e}')
        print(traceback.format_exc())
        return []
