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

    # El título de la pregunta es el nombre de columna del DataFrame, así que
    # tiene que ser único. La sección "Gestión de residuos" rompe ese supuesto:
    # sus cuatro grupos (Plásticos y electrónicos, Electrónicos, Residuos
    # peligrosos, Desechos) repiten los títulos 'Cantidad', 'Destino',
    # 'Detalle de residuo' y 'Número serial'. Al aplanar por título, cada grupo
    # sobreescribía al anterior y solo sobrevivía el último de 'answers'.
    # Solución: a las preguntas que viven DENTRO de un grupo y cuyo título se
    # repite en el formulario se les antepone el título del grupo, con la misma
    # convención ' | ' que ya usa Connecteam ('1.2.1 MC | Modelo').
    # Las preguntas de nivel raíz no se tocan, de modo que los títulos
    # duplicados de control ('¿Se interviene otro dispositivo?' y similares, que
    # el pipeline ignora) conservan el nombre de columna que tenían.
    conteo_titulos = {}

    def contar_titulos(q_list):
        for q in q_list:
            titulo = q.get('title')
            conteo_titulos[titulo] = conteo_titulos.get(titulo, 0) + 1
            if 'questions' in q:
                contar_titulos(q['questions'])

    contar_titulos(questions)

    def map_questions(q_list, titulo_grupo=None):
        for q in q_list:
            titulo = q['title']
            if titulo_grupo is not None and conteo_titulos.get(titulo, 0) > 1:
                titulo = f"{titulo_grupo} | {titulo}"
            question_id_to_title[q['questionId']] = titulo
            # Si es un grupo, mirar adentro recursivamente
            if 'questions' in q:
                map_questions(q['questions'], q['title'])
    
    map_questions(questions)

    # --- 2. Función Auxiliar para extraer valores (La misma lógica robusta) ---
    def _tiene_dato(answer_obj):
        # ¿La respuesta trae algún dato real, sin importar las marcas?
        return bool(
            answer_obj.get('value')
            or answer_obj.get('selectedAnswers')
            or answer_obj.get('selectedIndex') is not None
            or answer_obj.get('timestamp')
            or answer_obj.get('images')
            or answer_obj.get('ratingValue') not in (None, '')
        )

    def extraer_valor(answer_obj):
        # 'wasHidden' marca preguntas ocultadas por la lógica condicional
        # (p.ej. punto no visitado, rama de tipo de trabajo no elegida).
        # PERO al editar una submission para cambiar la rama condicional
        # (p.ej. corregir de I a CF y trasvasar las respuestas), Connecteam no
        # reevalúa la visibilidad y devuelve las casillas ya rellenadas con
        # wasHidden=True. Por eso solo descartamos cuando además NO hay dato
        # real (mismo criterio que wasSubmittedEmpty más abajo).
        if answer_obj.get('wasHidden', False) and not _tiene_dato(answer_obj):
            return None
        # Una pregunta agregada al formulario DESPUÉS del envío llega con
        # wasSubmittedEmpty=True aunque la submission se haya editado luego y
        # tenga un 'value' real. Solo la descartamos si está realmente vacía.
        if answer_obj.get('wasSubmittedEmpty', False) and not _tiene_dato(answer_obj):
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
                    # Devuelve objeto date para que Excel lo reconozca como fecha real
                    # (evita interpretación mm/dd ambigua según locale de Excel).
                    return dt_chile.date()
                except:
                    return 'Error Fecha'
            return None
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
        
        # Un questionType no contemplado se descartaba sin dejar rastro: el
        # pipeline corría "en verde" y el campo simplemente no aparecía en el
        # Excel. Avisamos para que un cambio de formulario sea visible.
        print(
            f"[ordenar_respuestas] questionType no soportado: {q_type!r} "
            f"(questionId={answer_obj.get('questionId')}). Respuesta descartada."
        )
        return None # Caso por defecto

    def recorrer_answers(lista, fila_datos):
        # El tipo 'group' trae una lista 'answers' directa, no 'groupAnswers'.
        # Se recorre en profundidad: hoy los grupos del formulario son de un solo
        # nivel, pero un grupo anidado dentro de otro llegaba a extraer_valor,
        # caía en el caso por defecto y se descartaba junto con todos sus hijos.
        for answer in lista:
            if answer.get('questionType') == 'group' and 'answers' in answer:
                recorrer_answers(answer['answers'], fila_datos)
                continue

            q_id = answer.get('questionId')
            titulo = question_id_to_title.get(q_id, f"Pregunta {q_id}")
            val = extraer_valor(answer)
            if val is not None:
                fila_datos[titulo] = val

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

        # Iterar sobre las respuestas principales (baja a los grupos anidados)
        recorrer_answers(submission.get('answers', []), fila_datos)

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
