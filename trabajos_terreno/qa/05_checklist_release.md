# 05 — Checklist de release

Lista de verificación previa al despliegue de un cambio en el pipeline.

## 1. Pre-requisitos de código

- [ ] El código se ejecuta sin error de importación en Python 3.11.9.
- [ ] `requirements.txt` actualizado si se añadieron dependencias.
- [ ] No se introdujeron credenciales ni secretos en el código fuente.

## 2. Pruebas funcionales

- [ ] Casos `TC-OR-*` (aplanado) ejecutados y aprobados.
- [ ] Casos `TC-CN-*` (deduplicación) ejecutados sobre SQLite temporal, no sobre la base de producción.
- [ ] Casos `TC-PE-*` cubren todos los tipos de trabajo afectados por el cambio.
- [ ] Casos `TC-EX-*` validan la inserción incremental sobre un Excel de prueba.
- [ ] Caso `TC-EX-04` confirma la alineación de columnas DataFrame ↔ tabla `OTS`.

## 3. Verificación de integridad de datos

- [ ] El orden de columnas de `data_terreno` coincide con la tabla `OTS`.
- [ ] Las columnas con espacio final (`Fecha visita `, `Fotos `) se referencian con el espacio.
- [ ] La columna `Fotos ` se elimina correctamente en inspecciones.
- [ ] El prefijo `III-` se aplica al número de OT.
- [ ] Las fechas quedan en `America/Santiago`.

## 4. Protección de producción

- [ ] Ninguna prueba escribió en el `Terreno.xlsx` de producción.
- [ ] `trabajos_terreno/form_entries.db` de producción no fue modificado por pruebas.
- [ ] Si se ejecutó `main_practice.py`, se confirmó que el destino era el entorno correcto.

## 5. CI/CD

- [ ] Secretos de GitHub Actions vigentes (`CONNECTEAM_API_KEY`, `MS_TENANT`, `MS_CLIENT_ID`, `MS_CLIENT_SECRET`).
- [ ] El workflow `main.yml` no presenta cambios no intencionados en el cron ni en los pasos de commit/push de la base.
- [ ] Tras el primer run posterior al cambio, verificar que el commit de `form_entries.db` se realizó y que el artefacto se subió.

## 6. Regresión por cambio de formulario

Si el cambio responde a una modificación del formulario en Connecteam:

- [ ] Verificar que los títulos de pregunta referenciados en `processor.py` siguen existiendo.
- [ ] Validar la nomenclatura de columnas (prefijos numéricos, ` TIPO (subtipo) | campo`).
- [ ] Reejecutar los casos de los tipos de trabajo afectados con submissions reales recientes.

## 7. Mejoras técnicas pendientes (registro)

Elementos identificados durante QA que conviene atender:

- [ ] Parametrizar la ruta de la base de datos en `check_new_sub` para facilitar las pruebas.
- [ ] Confirmar la carga a SharePoint **antes** de insertar IDs en `processed_entries`, para evitar OT marcadas como procesadas tras un fallo de carga.
- [ ] Implementar el reintento efectivo en `upload_file` ante archivo bloqueado (423).
- [ ] Validar cabeceras antes de la escritura posicional en Excel.
- [x] Reconciliar la documentación del processor con el código vigente (resuelto: integrada y corregida en `general_doc/07_processor_detalle.md`; la lógica `CI`/reclasificación inexistente queda documentada como tal).
- [ ] Documentar/abordar la limitación de 9 puntos por OT (`col[0]`).
