import re
import base64
import traceback
import pandas as pd
import numpy as np
from datetime import datetime
from connecteam_api import user



def process_entrys(ordered_responses, API_key_c):
    
    datos_terreno = []
    datos_inspeccion = []
    # Fotos a nivel de punto ({i}.4 Fotos recinto), indexadas por (OT, punto)
    # para adjuntarlas luego a cada fila de data_terreno sin tocar cada dict.
    fotos_por_caso = {}
    for i, r in ordered_responses.iterrows():

        r_clean = r.dropna()
        
        df = r_clean.to_frame().T #Transformamos la serie en un dataframe

        df_columnas = df.columns.to_list() #Lista de columnas que si tienen datos

        # df = df.astype({'user': str}) #Dejamos al id del user como string
        index_user = df.columns.get_loc('user') #Obtenemos la posición de la columna user

        try:
            user_name = user(API_key_c, df.iloc[0, index_user])
        except Exception as e:
            user_name = "Usuario no encontrado"
            print(f"Error al obtener el nombre del usuario: {e}")
            traceback.print_exc()
        
        try:
            df.iloc[0, index_user] = user_name # Añadir el nombre del usuario al DataFrame
        except Exception as e:
            print(f"Error al asignar el nombre del usuario al DataFrame: {e}")
            traceback.print_exc()


        # Agrupación para las visitas de inspección
        if df['Tipo de visita realizada'].item() == '(R) Ronda diaria de Inspección':
            # print(df_columnas)
    
            # print(df.columns.to_list())
            datos_inspeccion.append(df)
            continue


        #Elementos globales
        id_tipo_de_trabajo = ['MP', 'MC', 'I', 'R', 'CF']

        MP_type = ['T', 'I']
        MP_translate = {
            'I': 'Dispositivo',
            'T': 'Tablero'
        }
        
        R_type = ['E', 'I']

        


        I_type = ['I', 'T', 'C'] 
        I_translate = {
                'I': 'dispositivo',
                'T': 'tablero',
                'C': 'Categoría'
            }
        
        id_mantencion = {'MC': 'Mantención Correctiva',
                        'MP': 'Mantención Preventiva',
                        'I': 'Instalación',
                        'R': 'Reemplazo/Extracción',
                        'CF': 'Configuración/Ajustes'}
        
        # intalaciones_interes = ['Tablero', 'Caudalímetro', 'Sensor de nivel', 'Sonda multiparamétrica', 'Otro']

        operators ={
            "Diego Marchant": 145,
            "Ángel Zamora": 181,
            "Camilo Sandoval": 138,
            "Cristopher Iglesias": 141,
            "David  Loncopan": 144,
            "Emir Navarro Crocci": 147,
            "Felipe Riquelme": 149,
            "Juan José López": 159,
            "Leonardo Gonzalez": 160,
            "Matías Pomar": 164,
            "Rodrigo López": 172,
            "Tomás Bustamante": 178,
            "Elías Sanchez": 5432
        }

        #Puntos que efectivamente se visitaron
        numeros_visita = set()
        for col in df_columnas:
            # Verificamos si el nombre de la columna comienza con un dígito
            if col and col[0].isdigit():
                # Extraemos el primer carácter (el número)
                numeros_visita.add(col[0])

        numeros_visita = sorted(list(numeros_visita))
        

        #AQUI ANALIZAMOS CADA PUNTO VISITADO

    

        for i in numeros_visita:

            #Separación de los trabajos realizados
            # OJO: df[col] es una Series de 1 fila, NO un string. Antes se hacía
            # df[col].split(',') dentro de un try, que SIEMPRE fallaba (Series no
            # tiene .split) y caía al except dejando la Series entera como
            # "tipos_realizados". Al iterarla más abajo se obtenía un único elemento
            # con todos los tipos juntos ("MC | ..., CF | ...") y split(' |')[0] se
            # quedaba solo con el PRIMER tipo, descartando los demás (p.ej. CF).
            # Por eso un punto con varios tipos solo generaba el registro del primero.
            valor_tipos = df[f'{i}.2 Tipo de trabajo a realizar'].iloc[0]
            tipos_realizados = [tipo.strip() for tipo in str(valor_tipos).split(',')]

            # Columnas del punto {1} | general
            columnas_visita = [columna for columna in df_columnas if columna.startswith(i)]
            #columnas_visita.append(f'{i} Proyecto') 
            if 'Indique el modelo y serial de los residuos retirados' in df_columnas:
                # columnas_visita = ['#','Contrato', 'Causa visita', 'user', 'Fecha visita ','Calidad del Servicio', 'Nombre del Cliente', 'PT (Permiso de trabajo)', 'DET (Análisis de Riesgos)', 'Cinco Pasos para Trabajar Seguro', 'Charla de 5 Minutos', 'Check List de Camioneta/ Somnolencia', 'AST', '¿Hubo retiro de residuos electrónicos o peligrosos defectuosos para gestión de correcta eliminación?', 'Indique el modelo y serial de los residuos retirados'] + columnas_visita 
                columnas_visita = ['#','Contrato', 'Causa visita', 'user', 'Fecha visita ','Calidad del Servicio', 'Nombre del Cliente', 'PT (Permiso de trabajo)', 'DET (Análisis de Riesgos)', 'Cinco Pasos para Trabajar Seguro', 'Charla de 5 Minutos', 'Check List de Camioneta/ Somnolencia', 'AST'] + columnas_visita 
            
            else:
                # columnas_visita = ['#','Contrato', 'Causa visita', 'user', 'Fecha visita ','Calidad del Servicio', 'Nombre del Cliente', 'PT (Permiso de trabajo)', 'DET (Análisis de Riesgos)', 'Cinco Pasos para Trabajar Seguro', 'Charla de 5 Minutos', 'Check List de Camioneta/ Somnolencia', 'AST', '¿Hubo retiro de residuos electrónicos o peligrosos defectuosos para gestión de correcta eliminación?'] + columnas_visita 
                columnas_visita = ['#','Contrato', 'Causa visita', 'user', 'Fecha visita ','Calidad del Servicio', 'Nombre del Cliente', 'PT (Permiso de trabajo)', 'DET (Análisis de Riesgos)', 'Cinco Pasos para Trabajar Seguro', 'Charla de 5 Minutos', 'Check List de Camioneta/ Somnolencia', 'AST'] + columnas_visita 
 
            #Dejando un dataframe a nivel de visita de punto
            df_visita = df[columnas_visita].copy()


            #Validando si el punto se encuentra seteadao en el listado de connecteam
            if df_visita[f'{i}.1 Punto de monitoreo'].iloc[0] == "No encontrado":
            
                #Creamos la columna proyecto
                try:
                    index_columna_punto_proyecto = df_visita.columns.get_loc(f'{i} Proyecto')
                    df_visita.loc[:, f"{i}.1 Proyecto"] = df_visita.iloc[0, index_columna_punto_proyecto]
                    
                    #Definimos el punto ingresado manaualmente como el verdadero
                    index_columna_punto_no = df_visita.columns.get_loc(f'{i}.1 Punto de monitoreo')
                    index_columna_punto_si = df_visita.columns.get_loc(f'{i}.1 Indicar nombre del punto')

                    df_visita.iloc[0, index_columna_punto_no] = df_visita.iloc[0, index_columna_punto_si]

                    del df_visita[f'{i}.1 Indicar nombre del punto']
                except Exception as e:
                    print(f"Error al procesar el punto de monitoreo en OT {df_visita['#']}: {e}")
                    # Si no se encuentra la columna, asignamos un valor por defecto
                    df_visita.loc[:, f"{i}.1 Proyecto"] = "Proyecto no especificado"
                    df_visita.loc[:, f"{i}.1 Punto de monitoreo"] = "Punto no especificado"
                    continue
                    

            else:
                #Buscando el indice de columna
                index_columna_punto = df_visita.columns.get_loc(f'{i}.1 Punto de monitoreo')

                #Definiendo el nombre del proyecto
                match = re.search(r"\[([^\]]*)\]", df_visita.iloc[0, index_columna_punto])
                if match:
                    df_visita.loc[:, f"{i}.1 Proyecto"] = match.group(1)
                else:
                    df_visita.loc[:, f"{i}.1 Proyecto"] = "Proyecto no especificado"
                                
                #Definiedo el nombre del punto
                df_visita.iloc[0, index_columna_punto] = re.sub(r"\[[^\]]*\]", "", df_visita.iloc[0, index_columna_punto]).strip() #Eliminando el nombre del proyecto

            #display(df_visita)

            #Definimos los ID de los tipos de trabajo realizados
            id_tipos_realizados = [item.split(' |')[0] for item in tipos_realizados]
            #id_tipos_realizados

            #Definimos los ID de tipos de trabajo de interes
            id_tipos_interes = []
            for tipo in id_tipos_realizados:
                if tipo in id_tipo_de_trabajo:
                    id_tipos_interes.append(tipo)
            id_tipos_interes #[MC, MP]
            
            #Cantidad de MP realizadas

            R_E_prefijo = set()
            for col in df_visita.columns:
                if ' R (E) |' in col:
                    prefix_end_index = col.find(' R (E) |') + 4
                    prefix = col[:prefix_end_index].strip()
                    R_E_prefijo.add(prefix)
            conteo_instancias_R_E = len(R_E_prefijo)

            # print(conteo_instancias_R_E)

            R_I_prefijo = set()
            for col in df_visita.columns:
                if ' R (I) |' in col:
                    prefix_end_index = col.find(' R (I) |') + 4
                    prefix = col[:prefix_end_index].strip()
                    R_I_prefijo.add(prefix)
            conteo_instancias_R_I = len(R_I_prefijo)

            # print(conteo_instancias_R_I)

            conteo_R = {
                'E': conteo_instancias_R_E,
                'I': conteo_instancias_R_I
            }

            E_prefijo = set()
            for col in df_visita.columns:
                if ' E |' in col:
                    prefix_end_index = col.find(' E |') + 4
                    prefix = col[:prefix_end_index].strip()
                    E_prefijo.add(prefix)
            conteo_instancias_E = len(E_prefijo)


            #Conteo de instalaciones de instrumentos
            I_I_prefijo = set()
            for col in df_visita.columns:
                if ' I (I) |' in col: 
                    # Extraemos el prefijo como '1.2.1 MP' o '1.2.2 MP'
                    prefix_end_index = col.find(' I (I) |') + 4 # Sumamos 4 para incluir ' MP'
                    prefix = col[:prefix_end_index].strip()
                    I_I_prefijo.add(prefix)
            
            conteo_instancias_I_I = len(I_I_prefijo)
        
            #Conteo en el contesto de los tableros
            I_T_prefijo = set()
            for col in df_visita.columns:
                if ' I (T) |' in col: 
                    # Extraemos el prefijo como '1.2.1 MP' o '1.2.2 MP'
                    prefix_end_index = col.find(' I (T) |') + 4 # Sumamos 4 para incluir ' MP'
                    prefix = col[:prefix_end_index].strip()
                    I_T_prefijo.add(prefix)
            
            conteo_instancias_I_T = len(I_T_prefijo)

            I_C_prefijo = set()
            for col in df_visita.columns:
                if ' I (C) |' in col: 
                    # Extraemos el prefijo como '1.2.1 MP' o '1.2.2 MP'
                    prefix_end_index = col.find(' I (C) |') + 4 # Sumamos 4 para incluir ' MP'
                    prefix = col[:prefix_end_index].strip()
                    I_C_prefijo.add(prefix)
            
            conteo_instancias_I_C = len(I_C_prefijo)


            conteo_I = {
                'I': conteo_instancias_I_I,
                'T': conteo_instancias_I_T,
                'C': conteo_instancias_I_C
            }


            #Conteo en el contexto de los instrumentos
            MP_I_prefijo = set()
            for col in df_visita.columns:
                if ' MP (I) |' in col: 
                    # Extraemos el prefijo como '1.2.1 MP' o '1.2.2 MP'
                    prefix_end_index = col.find(' MP (I) |') + 4 # Sumamos 4 para incluir ' MP'
                    prefix = col[:prefix_end_index].strip()
                    MP_I_prefijo.add(prefix)
            
            conteo_instancias_MP_I = len(MP_I_prefijo)
        
            #Conteo en el contesto de los tableros
            MP_T_prefijo = set()
            for col in df_visita.columns:
                if ' MP (T) |' in col: 
                    # Extraemos el prefijo como '1.2.1 MP' o '1.2.2 MP'
                    prefix_end_index = col.find(' MP (T) |') + 4 # Sumamos 4 para incluir ' MP'
                    prefix = col[:prefix_end_index].strip()
                    MP_T_prefijo.add(prefix)
            
            conteo_instancias_MP_T = len(MP_T_prefijo)

            conteo_MP = {
                'I': conteo_instancias_MP_I,
                'T': conteo_instancias_MP_T
            }

            #Cantidad de MC realizadas
            MC_prefijo = set()
            for col in df_visita.columns:
                if ' MC |' in col: # Buscamos ' MC |' para identificar las columnas de MC
                    # Extraemos el prefijo como '1.2.1 MC' o '1.2.2 MC'
                    prefix_end_index = col.find(' MC |') + 4 # Sumamos 4 para incluir ' MC'
                    prefix = col[:prefix_end_index].strip()
                    MC_prefijo.add(prefix)
                    
            conteo_instancias_MC = len(MC_prefijo)


            #Cantidad de CF realizadas
            CF_prefijo = set()
            for col in df_visita.columns:
                if ' CF |' in col: # Buscamos ' CF |' para identificar las columnas de CF
                    # Extraemos el prefijo 
                    prefix_end_index = col.find(' CF |') + 4 # Sumamos 4 para incluir ' CF'
                    prefix = col[:prefix_end_index].strip()
                    CF_prefijo.add(prefix)
                    
            conteo_instancias_CF = len(CF_prefijo)


            #Cantidad de CI realizadas
            CI_prefijo = set()
            for col in df_visita.columns:
                if ' CI |' in col: # Buscamos ' CI |' para identificar las columnas de CI
                    # Extraemos el prefijo 
                    prefix_end_index = col.find(' CI |') + 4 # Sumamos 4 para incluir ' CI'
                    prefix = col[:prefix_end_index].strip()
                    CI_prefijo.add(prefix)
                    
            conteo_instancias_CI = len(CI_prefijo)


            #Cantidad de SO realizadas
            SO_prefijo = set()
            for col in df_visita.columns:
                if ' SO |' in col: # Buscamos ' SO |' para identificar las columnas de SO
                    # Extraemos el prefijo 
                    prefix_end_index = col.find(' SO |') + 4 # Sumamos 4 para incluir ' SO'
                    prefix = col[:prefix_end_index].strip()
                    SO_prefijo.add(prefix)
                    
            conteo_instancias_SO = len(SO_prefijo)

            # display(df_visita)

            #Variables globales
            proyecto = df_visita[f"{i}.1 Proyecto"].to_list()[0]
            punto = df_visita[f'{i}.1 Punto de monitoreo'].to_list()[0]
            ot = 'III-' + str(df_visita['#'].to_list()[0])
            contrato = df_visita['Contrato'].to_list()[0]
            fecha = df_visita['Fecha visita '].to_list()[0]
            tecnico = df_visita['user'].to_list()[0].strip()
            cliente = df_visita['Nombre del Cliente'].to_list()[0]
            causa_visita = df_visita['Causa visita'].to_list()[0]
            pt = df_visita['PT (Permiso de trabajo)'].to_list()[0]
            det = df_visita['DET (Análisis de Riesgos)'].to_list()[0]
            cinco_pasos = df_visita['Cinco Pasos para Trabajar Seguro'].to_list()[0]
            charla = df_visita['Charla de 5 Minutos'].to_list()[0]
            camioneta = df_visita['Check List de Camioneta/ Somnolencia'].to_list()[0]
            ast = df_visita['AST'].to_list()[0]
            resolución = df_visita[f'{i}.3 Resolución de visita'].to_list()[0]
            calidad = df_visita['Calidad del Servicio'].to_list()[0]

            # Fotos del recinto (nivel punto): lista de URLs o []. Se comparten
            # entre todos los trabajos del mismo punto. Se usan para el informe PDF.
            col_fotos = f'{i}.4 Fotos recinto'
            val_fotos = df_visita[col_fotos].iloc[0] if col_fotos in df_visita.columns else None
            fotos_punto = list(val_fotos) if isinstance(val_fotos, (list, tuple)) else []
            fotos_por_caso[(ot, punto)] = fotos_punto
            #residuo = df_visita['¿Hubo retiro de residuos electrónicos o peligrosos defectuosos para gestión de correcta eliminación?'].to_list()[0]
            #tipo_residuo = df_visita['Indique el modelo y serial de los residuos retirados'].to_list()[0] if residuo == 'Sí' else None



            for id in id_tipos_realizados:
                columnas_trabajo = [columna for columna in df_visita.columns if f'{id}' in columna or "E" in columna]
                # columnas_trabajo = ['#', 'user', f"{i}.1 Proyecto", 'Fecha visita ', 'Nombre del Cliente'] + columnas_trabajo
                df_trabajo = df_visita[columnas_trabajo]

                #Tratamiento para reemplazos

                if id == "R":

                    #Reemplazo completo
                    for t in R_type:
                        for equipo in range(1, conteo_R[t]+1):
                 
                            filtro_general = f"{i}.2.{equipo} R"
                            columnas_general = df_trabajo.filter(like=filtro_general).columns.to_list()

                            filtro_R_E = f"{i}.2.{equipo} R ({t})"        
                            columnas_R_E = df_trabajo.filter(like=filtro_R_E).columns.to_list()


                            # columnas_general ya incluye las columnas "R (E)"/"R (I)",
                            # así que concatenar columnas_R_E las repetía → DataFrame con
                            # columnas duplicadas y UserWarning al hacer to_dict. Deduplicamos
                            # preservando el orden.
                            columnas_equipo_R = list(dict.fromkeys(columnas_general + columnas_R_E))


                            # df trabajo se usa para la generación del informe
                            df_trabajo_equipo_R = df_trabajo[columnas_equipo_R]
                            dic_trabajo_R = df_trabajo_equipo_R.to_dict(orient='records')[0]

                            # Elmentos propios del equipo
                            modelo_R = dic_trabajo_R[f"{filtro_R_E} | Modelo"]
                            tipo_R = dic_trabajo_R[f"{filtro_general} | Tipo equipo/instrumento a reemplazar"]
                            serial_R = dic_trabajo_R[f'{filtro_R_E} | N° de serie']
                            obs_R = dic_trabajo_R[f'{filtro_general} | Observación']
                            alcance_R = dic_trabajo_R[f'{filtro_general} | Motivo de reemplazo']
                            destino_R = dic_trabajo_R[f'{filtro_R_E} | Destino'] if t == "E" else None
                            trabajo_R = t



                            datos_terreno.append({
                                'OT': ot,
                                'Técnico': tecnico,
                                'Contrato': contrato,
                                'Causa visita': causa_visita,
                                'Proyecto': proyecto,
                                'Asset': punto,
                                'Tipo de trabajo': trabajo_R,
                                'Fecha visita': fecha,
                                'Cliente': cliente,
                                'Resolución visita': resolución,
                                'Calidad del Servicio': calidad,
                                "PT (Permiso de trabajo)": pt,
                                "DET (Análisis de Riesgos)": det,
                                "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                                "Charla de 5 Minutos": charla,
                                "Check List de Camioneta/ Somnolencia": camioneta,
                                "AST": ast,
                                'Observación': obs_R,
                                'Equipo': tipo_R,
                                'Modelo': modelo_R,
                                'N° serie': serial_R,
                                'Alcance': alcance_R
                            })

                    #Solo extracción
                    for equipo in range(1,conteo_instancias_E+1):
                            filtro_E = f"{i}.2.{equipo} E"        
                            columnas_E = df_trabajo.filter(like=filtro_E).columns.to_list()


                            df_trabajo_equipo_E = df_trabajo[columnas_E]

                            dic_trabajo_E = df_trabajo_equipo_E.to_dict(orient='records')[0]
                            # Elmentos propios del equipo
                            modelo_E = dic_trabajo_E[f"{filtro_E} | Modelo"]
                            tipo_E = dic_trabajo_E[f"{filtro_E} | Tipo equipo/instrumento a extraer"]
                            serial_E = dic_trabajo_E[f'{filtro_E} | N° de serie']
                            obs_E = dic_trabajo_E[f'{filtro_E} | Observación']
                            alcance_E = dic_trabajo_E[f'{filtro_E} | Motivo de extracción']

                            datos_terreno.append({
                                'OT': ot,
                                'Técnico': tecnico,
                                'Contrato': contrato,
                                'Causa visita': causa_visita,
                                'Proyecto': proyecto,
                                'Asset': punto,
                                'Tipo de trabajo': "E" ,
                                'Fecha visita': fecha,
                                'Cliente': cliente,
                                'Resolución visita': resolución,
                                'Calidad del Servicio': calidad,
                                "PT (Permiso de trabajo)": pt,
                                "DET (Análisis de Riesgos)": det,
                                "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                                "Charla de 5 Minutos": charla,
                                "Check List de Camioneta/ Somnolencia": camioneta,
                                "AST": ast,
                                'Observación': obs_E,
                                'Equipo': tipo_E,
                                'Modelo': modelo_E,
                                'N° serie': serial_E,
                                'Alcance': alcance_E
                            })




                #Tratamiento para Mantención correctiva
                elif id == "MC":
                    for equipo in range(1, conteo_instancias_MC+1):
                        filtro_MC = f"{i}.2.{equipo} MC"        
                        columnas_equipo_MC = df_trabajo.filter(like=filtro_MC).columns.to_list()
                        
                        df_trabajo_equipo_MC = df_trabajo[columnas_equipo_MC]
                        dic_trabajo_MC = df_trabajo_equipo_MC.to_dict(orient='records')[0]

                        #Elmentos propios del equipo
                        modelo_MC = dic_trabajo_MC[f"{i}.2.{equipo} MC | Modelo"]
                        tipo_MC = dic_trabajo_MC[f"{i}.2.{equipo} MC | Activo a intervenir"]
                        serial_MC = dic_trabajo_MC[f'{i}.2.{equipo} MC | N° de serie']
                        operativo_MC = dic_trabajo_MC[f"{i}.2.{equipo} MC | ¿Equipo operativo tras trabajos?"]
                        obs_MC = dic_trabajo_MC[f'{i}.2.{equipo} MC | Observación']
                        alcance_MC = None


                        
                        datos_terreno.append({
                            'OT': ot,
                            'Técnico': tecnico,
                            'Contrato': contrato,
                            'Causa visita': causa_visita,
                            'Proyecto': proyecto,
                            'Asset': punto,
                            'Tipo de trabajo': id,
                            'Fecha visita': fecha,
                            'Cliente': cliente,
                            'Resolución visita': resolución,
                            'Calidad del Servicio': calidad,
                            "PT (Permiso de trabajo)": pt,
                            "DET (Análisis de Riesgos)": det,
                            "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                            "Charla de 5 Minutos": charla,
                            "Check List de Camioneta/ Somnolencia": camioneta,
                            "AST": ast,
                            'Observación': obs_MC,
                            'Equipo': tipo_MC,
                            'Modelo': modelo_MC,
                            'N° serie': serial_MC,
                            'Alcance': alcance_MC,
                            #'Residuo': residuo,
                            #'Tipo de residuo': tipo_residuo
                        })
                
                elif id == 'CF':
                    for equipo in range(1, conteo_instancias_CF+1):
                        filtro_CF = f"{i}.2.{equipo} CF"        
                        columnas_equipo_CF = df_trabajo.filter(like=filtro_CF).columns.to_list()
                        
                        df_trabajo_equipo_CF = df_trabajo[columnas_equipo_CF]
                        dic_trabajo_CF = df_trabajo_equipo_CF.to_dict(orient='records')[0]

                        #Elmentos propios del equipo
                        modelo_CF = dic_trabajo_CF[f"{i}.2.{equipo} CF | Modelo"]
                        tipo_CF = dic_trabajo_CF[f"{i}.2.{equipo} CF | Activo a intervenir"]
                        serial_CF = dic_trabajo_CF[f'{i}.2.{equipo} CF | N° de serie']
                        operativo_CF = dic_trabajo_CF[f"{i}.2.{equipo} CF | ¿Equipo operativo tras trabajos?"]
                        obs_CF = dic_trabajo_CF[f'{i}.2.{equipo} CF | Observación']
                        alcance_CF = dic_trabajo_CF[f'{i}.2.{equipo} CF | Tipo de Ajuste']

                        datos_terreno.append({
                            'OT': ot,
                            'Técnico': tecnico,
                            'Contrato': contrato,
                            'Causa visita': causa_visita,
                            'Proyecto': proyecto,
                            'Asset': punto,
                            'Tipo de trabajo': id,
                            'Fecha visita': fecha,
                            'Cliente': cliente,
                            'Resolución visita': resolución,
                            'Calidad del Servicio': calidad,
                            "PT (Permiso de trabajo)": pt,
                            "DET (Análisis de Riesgos)": det,
                            "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                            "Charla de 5 Minutos": charla,
                            "Check List de Camioneta/ Somnolencia": camioneta,
                            "AST": ast,
                            'Observación': obs_CF,
                            'Equipo': tipo_CF,
                            'Modelo': modelo_CF,
                            'N° serie': serial_CF,
                            'Alcance': alcance_CF,
                            #'Residuo': residuo,
                            #'Tipo de residuo': tipo_residuo
                        })
                
                elif id == "I":
                        #Iteramos sobre los tipos de mantenimientos

                    for t in I_type:

                        #Itereramos sobre la cantidad de intalaciones del tipo t que se realizaron

                        for equipo in range(1, conteo_I[t]+1):

                            filtro_I = f"{i}.2.{equipo} I ({t})"        
                            columnas_equipo_I = df_trabajo.filter(like=filtro_I).columns.to_list()
                            
                        #   df trabajo se usa para la generación del informe
                            df_trabajo_equipo_I = df_trabajo[columnas_equipo_I]
                            dic_trabajo_I = df_trabajo_equipo_I.to_dict(orient='records')[0]
                        #  Elmentos propios del equipo
                        #  Usamos .get(...) porque una pregunta agregada en Connecteam DESPUÉS
                        #  del submit no existe en las submissions viejas (la API no la rellena),
                        #  y el tipo 'C' (Categoría) no incluye varios de estos campos por diseño.
                            modelo_I = dic_trabajo_I.get(f"{i}.2.{equipo} I ({t}) | Modelo")
                            tipo_I = dic_trabajo_I.get(f"{i}.2.{equipo} I ({t}) | Tipo de {I_translate[t]}") if t != 'C' else dic_trabajo_I.get(f"{i}.2.{equipo} I ({t}) | {I_translate[t]}")
                            serial_I = dic_trabajo_I.get(f'{i}.2.{equipo} I ({t}) | N° de serie')
                            operativo_I = dic_trabajo_I.get(f"{i}.2.{equipo} I ({t}) | ¿Equipo operativo tras trabajos?") if t != 'C' else False
                            obs_I = dic_trabajo_I.get(f'{i}.2.{equipo} I ({t}) | Observación')
                            alcance_I = 'IH | Habilitación de equipo' if t != 'T' else dic_trabajo_I.get(f"{i}.2.{equipo} I ({t}) | Alcance de la intervención")

                            datos_terreno.append({
                                'OT': ot,
                                'Técnico': tecnico,
                                'Contrato': contrato,
                                'Causa visita': causa_visita,
                                'Proyecto': proyecto,
                                'Asset': punto,
                                'Tipo de trabajo': id,
                                'Fecha visita': fecha,
                                'Cliente': cliente,
                                'Resolución visita': resolución,
                                'Calidad del Servicio': calidad,
                                "PT (Permiso de trabajo)": pt,
                                "DET (Análisis de Riesgos)": det,
                                "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                                "Charla de 5 Minutos": charla,
                                "Check List de Camioneta/ Somnolencia": camioneta,
                                "AST": ast,
                                'Observación': obs_I,
                                'Equipo': tipo_I,
                                'Modelo': modelo_I,
                                'N° serie': serial_I,
                                'Alcance': alcance_I,
                                # 'Residuo': residuo,
                                # 'Tipo de residuo': tipo_residuo
                            })
                    
                elif id == "MP":
                    # Iteramos sobre los tipos de mantenimientos
                    for t in MP_type:

                        for equipo in range(1, conteo_MP[t]+1):

                            filtro_MP = f"{i}.2.{equipo} MP ({t})"        
                            columnas_equipo_MP = df_trabajo.filter(like=filtro_MP).columns.to_list()
                            
                            # df trabajo se usa para la generación del informe
                            df_trabajo_equipo_MP = df_trabajo[columnas_equipo_MP]
                            dic_trabajo_MP = df_trabajo_equipo_MP.to_dict(orient='records')[0]

                            # Elmentos propios del equipo
                            modelo_MP = dic_trabajo_MP[f"{i}.2.{equipo} MP ({t}) | Modelo"]
                            tipo_MP = dic_trabajo_MP[f"{i}.2.{equipo} MP ({t}) | {MP_translate[t]} a intervenir"]
                            serial_MP = dic_trabajo_MP[f'{i}.2.{equipo} MP ({t}) | N° de serie']
                            operativo_MP = dic_trabajo_MP[f"{i}.2.{equipo} MP ({t}) | ¿{MP_translate[t]} operativo tras trabajos?"]
                            obs_MP = dic_trabajo_MP[f'{i}.2.{equipo} MP ({t}) | Observación']
                            alcance_MP = None

                            datos_terreno.append({
                                'OT': ot,
                                'Técnico': tecnico,
                                'Contrato': contrato,
                                'Causa visita': causa_visita,
                                'Proyecto': proyecto,
                                'Asset': punto,
                                'Tipo de trabajo': id,
                                'Fecha visita': fecha,
                                'Cliente': cliente,
                                'Resolución visita': resolución,
                                'Calidad del Servicio': calidad,
                                "PT (Permiso de trabajo)": pt,
                                "DET (Análisis de Riesgos)": det,
                                "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                                "Charla de 5 Minutos": charla,
                                "Check List de Camioneta/ Somnolencia": camioneta,
                                "AST": ast,
                                'Observación': obs_MP,
                                'Equipo': tipo_MP,
                                'Modelo': modelo_MP,
                                'N° serie': serial_MP,
                                'Alcance': alcance_MP,
                                # 'Residuo': residuo,
                                # 'Tipo de residuo': tipo_residuo
                            })

                elif id == 'SO':
                    for equipo in range(1, conteo_instancias_SO+1):
                        filtro_SO = f"{i}.2.{equipo} SO"        
                        columnas_equipo_SO = df_trabajo.filter(like=filtro_SO).columns.to_list()
                        
                        #df trabajo se usa para la generación del informe
                        df_trabajo_equipo_SO = df_trabajo[columnas_equipo_SO]
                        dic_trabajo_SO = df_trabajo_equipo_SO.to_dict(orient='records')[0]

                        #Elmentos propios del equipo
                        alcance_SO = dic_trabajo_SO[f"{i}.2.{equipo} SO | Tipo de solicitud"]
                        obs_SO = dic_trabajo_SO[f"{i}.2.{equipo} SO | Observación"]

                        datos_terreno.append({
                            'OT': ot,
                            'Técnico': tecnico,
                            'Contrato': contrato,
                            'Causa visita': causa_visita,
                            'Proyecto': proyecto,
                            'Asset': punto,
                            'Tipo de trabajo': id,
                            'Fecha visita': fecha,
                            'Cliente': cliente,
                            'Resolución visita': resolución,
                            'Calidad del Servicio': calidad,
                            "PT (Permiso de trabajo)": pt,
                            "DET (Análisis de Riesgos)": det,
                            "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                            "Charla de 5 Minutos": charla,
                            "Check List de Camioneta/ Somnolencia": camioneta,
                            "AST": ast,
                            'Observación': obs_SO,
                            'Equipo': None,
                            'Modelo': None,
                            'N° serie': None,
                            'Alcance': alcance_SO,
                            # 'Residuo': residuo,
                            # 'Tipo de residuo': tipo_residuo
                        })
                
                elif id == 'LT':
                    datos_terreno.append({
                        'OT': ot,
                        'Técnico': tecnico,
                        'Contrato': contrato,
                        'Causa visita': causa_visita,
                        'Proyecto': proyecto,
                        'Asset': punto,
                        'Tipo de trabajo': id,
                        'Fecha visita': fecha,
                        'Cliente': cliente,
                        'Resolución visita': resolución,
                        'Calidad del Servicio': calidad,
                        "PT (Permiso de trabajo)": pt,
                        "DET (Análisis de Riesgos)": det,
                        "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                        "Charla de 5 Minutos": charla,
                        "Check List de Camioneta/ Somnolencia": camioneta,
                        "AST": ast,
                        'Observación': None,
                        'Equipo': None,
                        'Modelo': None,
                        'N° serie': None,
                        'Alcance': None,
                        # 'Residuo': residuo,
                        # 'Tipo de residuo': tipo_residuo
                    })
                
                elif id == 'C':
                    datos_terreno.append({
                        'OT': ot,
                        'Técnico': tecnico,
                        'Contrato': contrato,
                        'Causa visita': causa_visita,
                        'Proyecto': proyecto,
                        'Asset': punto,
                        'Tipo de trabajo': id,
                        'Fecha visita': fecha,
                        'Cliente': cliente,
                        'Resolución visita': resolución,
                        'Calidad del Servicio': calidad,
                        "PT (Permiso de trabajo)": pt,
                        "DET (Análisis de Riesgos)": det,
                        "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                        "Charla de 5 Minutos": charla,
                        "Check List de Camioneta/ Somnolencia": camioneta,
                        "AST": ast,
                        'Observación': None,
                        'Equipo': None,
                        'Modelo': None,
                        'N° serie': None,
                        'Alcance': None,
                        # 'Residuo': residuo,
                        # 'Tipo de residuo': tipo_residuo
                    })

                elif id == 'G':
                    datos_terreno.append({
                        'OT': ot,
                        'Técnico': tecnico,
                        'Contrato': contrato,
                        'Causa visita': causa_visita,
                        'Proyecto': proyecto,
                        'Asset': punto,
                        'Tipo de trabajo': id,
                        'Fecha visita': fecha,
                        'Cliente': cliente,
                        'Resolución visita': resolución,
                        'Calidad del Servicio': calidad,
                        "PT (Permiso de trabajo)": pt,
                        "DET (Análisis de Riesgos)": det,
                        "Cinco Pasos para Trabajar Seguro": cinco_pasos,
                        "Charla de 5 Minutos": charla,
                        "Check List de Camioneta/ Somnolencia": camioneta,
                        "AST": ast,
                        'Observación': None,
                        'Equipo': None,
                        'Modelo': None,
                        'N° serie': None,
                        'Alcance': None,
                        # 'Residuo': residuo,
                        # 'Tipo de residuo': tipo_residuo
                    })
    
    # Generación de dataframe con los trabajos en terreno realizados
    df_final_terreno = pd.DataFrame(datos_terreno)

    # Columna auxiliar interna con las fotos del punto (para el informe PDF).
    # Es interna: report_manager la consume y la elimina antes de escribir a Excel.
    if not df_final_terreno.empty:
        df_final_terreno['_fotos'] = [
            fotos_por_caso.get((ot, asset), [])
            for ot, asset in zip(df_final_terreno['OT'], df_final_terreno['Asset'])
        ]

    # Generación de dataframe con las visitas de inspección realizadas

    if datos_inspeccion:
        df_final_inspeccion = pd.concat(datos_inspeccion, ignore_index=True)
    else:
        df_final_inspeccion = pd.DataFrame()
    

    # --- Expansión por "puntos visitados" ---
    # Cada registro cuya columna "puntos visitados" contiene un string "a,b,c,..."
    # se expande en tantas filas como puntos tenga, asignando un punto individual por fila.
    COLUMNA_PUNTOS = "Puntos visitados"

    if COLUMNA_PUNTOS in df_final_inspeccion.columns and not df_final_inspeccion.empty:
        filas_expandidas = []
        for _, fila in df_final_inspeccion.iterrows():
            puntos_raw = fila[COLUMNA_PUNTOS]
            if pd.notna(puntos_raw) and "," in str(puntos_raw):
                puntos_lista = [p.strip() for p in str(puntos_raw).split(",") if p.strip()]
                for punto in puntos_lista:
                    fila_nueva = fila.copy()
                    fila_nueva[COLUMNA_PUNTOS] = punto
                    filas_expandidas.append(fila_nueva)
            else:
                filas_expandidas.append(fila)

        df_final_inspeccion = pd.DataFrame(filas_expandidas).reset_index(drop=True)
        df_final_inspeccion = df_final_inspeccion.drop(columns=['Fotos '])

    else:
        print(df_final_inspeccion.columns.to_list())

    # Ordenamiento por fecha descendente (más reciente primero) para que al
    # insertar arriba en la tabla de Excel queden cronológicamente ordenados.
    if not df_final_terreno.empty and 'Fecha visita' in df_final_terreno.columns:
        df_final_terreno = df_final_terreno.sort_values(
            by='Fecha visita', ascending=False, na_position='last', kind='stable'
        ).reset_index(drop=True)

    if not df_final_inspeccion.empty and 'Fecha visita ' in df_final_inspeccion.columns:
        df_final_inspeccion = df_final_inspeccion.sort_values(
            by='Fecha visita ', ascending=False, na_position='last', kind='stable'
        ).reset_index(drop=True)

    # --- Alineación con los encabezados de Excel ---
    # La escritura en SharePoint es por NOMBRE de columna (ver excel_manager),
    # por lo que aquí dejamos las columnas con el nombre EXACTO del encabezado
    # de cada tabla.

    # Terreno (tabla OTS): el único nombre que difiere del encabezado es la
    # serie ('N° serie' en el dict vs 'N° de serie' en Excel).
    if not df_final_terreno.empty:
        df_final_terreno = df_final_terreno.rename(columns={'N° serie': 'N° de serie'})

    # Inspección (tabla Ronda): las columnas vienen con los títulos crudos del
    # formulario Connecteam; los traducimos a los encabezados de la tabla y
    # fijamos el orden/conjunto de columnas (las que no existan quedan vacías,
    # p.ej. 'Fotos', que se descarta aguas arriba).
    MAPEO_INSPECCION = {
        '#': 'OT',
        'user': 'Técnico',
        'fecha_envio': 'Fecha envío',
        'Contrato': 'Contrato',
        'Fecha visita ': 'Fecha ronda',
        'Causa visita': 'Causa',
        'Tipo de visita realizada': 'Tipo de trabajo',
        '¿Hubo residuos?': 'Retiro de residuos',
        'Nombre del Cliente': 'Cliente',
        'Calidad del Servicio': 'Calidad del servicio',
        'Puntos visitados': 'Puntos visitados',
        'Resolución ronda de inspección': 'Resumen',
    }
    HEADERS_RONDA = [
        'OT', 'Técnico', 'Fecha envío', 'Contrato', 'Fecha ronda', 'Causa',
        'Tipo de trabajo', 'Retiro de residuos', 'Cliente', 'Calidad del servicio',
        'Puntos visitados', 'Resumen', 'Fotos',
    ]
    if not df_final_inspeccion.empty:
        df_final_inspeccion = (
            df_final_inspeccion.rename(columns=MAPEO_INSPECCION)
            .reindex(columns=HEADERS_RONDA)
        )

    return df_final_terreno, df_final_inspeccion