# 01 — Estrategia de QA

## 1. Objetivo

Garantizar que cada submission válida de Connecteam se transforme en los registros
correctos en las tablas `OTS` y `Ronda` de `Terreno.xlsx`, sin duplicaciones, sin pérdida
de datos y respetando la nomenclatura y los tipos esperados.

## 2. Alcance

### En alcance

- Aplanado de submissions (`ordenar_respuestas`).
- Deduplicación (`check_new_sub`) y su efecto sobre `form_entries.db`.
- Normalización por tipo de trabajo y por punto (`process_entrys`).
- Expansión de rondas de inspección por punto.
- Lógica de escritura incremental en Excel (`modify_excel_file`), validada con archivos
  locales de prueba.

### Fuera de alcance (verificación manual / monitoreo)

- Disponibilidad real de la API de Connecteam y de Microsoft Graph.
- Corrección de las credenciales y secretos.
- Comportamiento de los dashboards que consumen `Terreno.xlsx`.

## 3. Niveles de prueba

| Nivel | Descripción | Dependencias externas |
| --- | --- | --- |
| Unitario | Funciones puras y de transformación con entradas controladas. | Simuladas (mock). |
| Integración | Encadenamiento `ordenar_respuestas` → `check_new_sub` → `process_entrys`. | SQLite temporal; API simulada. |
| Sistema (manual) | Ejecución de `main_practice.py` contra OT reales hacia un Excel de prueba. | Connecteam real; SharePoint de prueba. |
| Regresión | Reejecución de los casos al modificar `processor.py` o el formulario. | Según el caso. |

## 4. Matriz de riesgos

| Riesgo | Impacto | Probabilidad | Mitigación de QA |
| --- | --- | --- | --- |
| Cambio en títulos de pregunta del formulario rompe el mapeo de columnas. | Alto | Media | Casos que validan presencia de columnas clave; prueba de regresión tras cambios de formulario. |
| Escritura posicional en Excel con orden de columnas desalineado. | Alto | Baja | Caso que compara cabeceras de DataFrame contra cabeceras de la tabla. |
| OT marcada como procesada pese a fallo de carga. | Alto | Media | Caso que verifica el orden inserción/carga y documenta el procedimiento de reenvío. |
| Más de 9 puntos en una OT (colisión en `col[0]`). | Medio | Baja | Caso límite documentado. |
| Más de 100 OT entre corridas quedan fuera de la ventana. | Medio | Baja | Monitoreo de volumen; caso de documentación. |
| Convención `yesNo` invertida produce valores incorrectos. | Medio | Baja | Caso unitario específico de `ordenar_respuestas`. |
| Usuario inactivo no resoluble por la API. | Bajo | Media | Caso que verifica fallback `"Usuario no encontrado"`. |

## 5. Criterios de aceptación general

- Todos los casos de severidad alta y media en estado "Aprobado".
- Sin regresiones en los tipos de trabajo previamente soportados.
- La base `form_entries.db` de producción no se modifica durante la ejecución de pruebas
  automatizadas.
- Ninguna prueba escribe en el `Terreno.xlsx` de producción.

## 6. Entorno de pruebas recomendado

- Python 3.11.9 con las dependencias de `requirements.txt`.
- `pytest` (a incorporar) para pruebas unitarias y de integración.
- Una copia de `Terreno.xlsx` en una ubicación de prueba para validar `modify_excel_file`
  sin tocar producción.
- Variables de entorno apuntando a credenciales y a un destino SharePoint de prueba para
  las pruebas de sistema.
