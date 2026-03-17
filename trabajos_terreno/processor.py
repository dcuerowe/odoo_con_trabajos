import re
import base64
import traceback
import pandas as pd
from datetime import datetime
from connecteam_api import user



def process_entrys(ordered_responses, API_key_c):
    
    datos = []
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


        #Elementos globales
        id_tipo_de_trabajo = ['MP', 'MC', 'I', 'CI', 'CF']

        MP_type = ['T', 'I']
        MP_translate = {
            'I': 'Dispositivo',
            'T': 'Tablero'
        }


        I_type = ['I', 'T'] 
        I_translate = {
                'I': 'dispositivo',
                'T': 'tablero'
            }
        
        id_mantencion = {'MC': 'Mantención Correctiva',
                        'MP': 'Mantención Preventiva',
                        'I': 'Instalación',
                        'CI': 'Calibración Instrumento',
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
            try: 
                tipos_realizados = [tipo.strip() for tipo in df[f'{i}.2 Tipo de trabajo a realizar'].split(',') ]
            except:
                tipos_realizados = df[f'{i}.2 Tipo de trabajo a realizar']

            # Columnas del punto {1} | general
            columnas_visita = [columna for columna in df_columnas if columna.startswith(i)]
            #columnas_visita.append(f'{i} Proyecto') 
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

            conteo_I = {
                'I': conteo_instancias_I_I,
                'T': conteo_instancias_I_T
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
                    prefix_end_index = col.find(' CF |') + 4 # Sumamos 4 para incluir ' CI'
                    prefix = col[:prefix_end_index].strip()
                    CF_prefijo.add(prefix)
                    
            conteo_instancias_CI = len(CI_prefijo)


            #Cantidad de CI realizadas
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
            ot = f"III-{df_visita['#'].to_list()[0]}"
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


            for id in id_tipos_realizados:
                columnas_trabajo = [columna for columna in df_visita.columns if f'{id}' in columna]
                # columnas_trabajo = ['#', 'user', f"{i}.1 Proyecto", 'Fecha visita ', 'Nombre del Cliente'] + columnas_trabajo
                df_trabajo = df_visita[columnas_trabajo]

                #Tratamiento para Mantención correctiva
                if id == "MC":
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


                        
                        datos.append({
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
                            'Alcance': alcance_MC
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

                        datos.append({
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
                            'Alcance': alcance_CF
                        })
                
                elif id == 'CI':
                    for equipo in range(1, conteo_instancias_CI+1):
                        filtro_CI = f"{i}.2.{equipo} CI"        
                        columnas_equipo_CI = df_trabajo.filter(like=filtro_CI).columns.to_list()
                        
                        #df trabajo se usa para la generación del informe
                        df_trabajo_equipo_CI = df_trabajo[columnas_equipo_CI]
                        dic_trabajo_CI = df_trabajo_equipo_CI.to_dict(orient='records')[0]

                        #Elmentos propios del equipo
                        alcance_CI = dic_trabajo_CI[f"{i}.2.{equipo} CI | Etapa"]
                        modelo_CI = dic_trabajo_CI[f"{i}.2.{equipo} CI | Modelo"]
                        tipo_CI = "Sonda multiparamétrica"
                        serial_CI = dic_trabajo_CI[f'{i}.2.{equipo} CI | N° de serie']
                        obs_CI = dic_trabajo_CI[f'{i}.2.{equipo} CI | Observación']

                        datos.append({
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
                            'Observación': obs_CI,
                            'Equipo': tipo_CI,
                            'Modelo': modelo_CI,
                            'N° serie': serial_CI,
                            'Alcance': alcance_CI
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
                            modelo_I = dic_trabajo_I[f"{i}.2.{equipo} I ({t}) | Modelo"]
                            tipo_I = dic_trabajo_I[f"{i}.2.{equipo} I ({t}) | Tipo de {I_translate[t]}"]
                            serial_I = dic_trabajo_I[f'{i}.2.{equipo} I ({t}) | N° de serie']
                            operativo_I = dic_trabajo_I[f"{i}.2.{equipo} I ({t}) | ¿Equipo operativo tras trabajos?"]
                            obs_I = dic_trabajo_I[f'{i}.2.{equipo} I ({t}) | Observación']
                            alcance_I = 'IH | Habilitación de equipo' if t == 'I' else dic_trabajo_I[f"{i}.2.{equipo} I ({t}) | Alcance de la intervención"]

                            datos.append({
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
                                'Alcance': alcance_I
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

                            datos.append({
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
                                'Alcance': alcance_MP
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

                        datos.append({
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
                            'Alcance': alcance_SO
                        })
                
                elif id == 'LT':
                    datos.append({
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
                        'Alcance': None
                    })
                
                elif id == 'C':
                    datos.append({
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
                        'Alcance': None
                    })
    
    df_final = pd.DataFrame(datos)

    return df_final    