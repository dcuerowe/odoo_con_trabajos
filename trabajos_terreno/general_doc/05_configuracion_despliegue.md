# 05 — Configuración y despliegue

## 1. Requisitos

- Python 3.11.9.
- Dependencias declaradas en `requirements.txt` (pandas, openpyxl, requests, msal,
  python-dotenv, certifi, tabulate, schedule, entre otras).

Instalación:

```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

## 2. Variables de entorno

Definidas en `.env` localmente y como secretos en GitHub Actions.

| Variable | Uso | Obligatoria |
| --- | --- | --- |
| `CONNECTEAM_API_KEY` | Autenticación a la API de Connecteam. | Sí |
| `MS_TENANT` | Tenant de Azure AD (autoridad MSAL). | Sí |
| `MS_CLIENT_ID` | Client ID de la aplicación registrada en Azure AD. | Sí |
| `MS_CLIENT_SECRET` | Secreto de cliente de la aplicación. | Sí |
| `sharepoint_user`, `sharepoint_password`, `sharepoint_url_site`, `sharepoint_site_name`, `sharepoint_doc_library` | Credenciales SharePoint legacy. | No (no todas en uso) |

Constantes fijadas en código (`config.py`): `FORM_ID` y `EXCEL_URL`.

## 3. Ejecución local

```bash
# Job automático (procesa solo OT nuevas según la base SQLite)
python trabajos_terreno/main.py

# Modo interactivo (reprocesa OT indicadas manualmente)
python trabajos_terreno/main_practice.py
```

El directorio de trabajo efectivo de la aplicación es `trabajos_terreno/`, ya que los
imports son planos (`from config import ...`) y `check_new_sub` resuelve la ruta de la
base de datos relativa al archivo del módulo.

## 4. CI/CD — GitHub Actions

Workflow: `.github/workflows/main.yml`.

| Atributo | Valor |
| --- | --- |
| Disparadores | `schedule` cron `0 9 * * 1-6` (lunes a sábado, 09:00 UTC) y `workflow_dispatch` (manual). |
| Runner | `ubuntu-latest`. |
| Permisos | `contents: write` (para commitear la base de datos). |
| Python | 3.11.9 con caché de pip. |

Pasos:

1. Checkout del repositorio.
2. Configuración de Python 3.11.9.
3. Instalación de dependencias (`--force-reinstall`).
4. Ejecución de `python trabajos_terreno/main.py` con los secretos como variables de entorno.
5. Configuración de identidad Git de la Action.
6. Commit de `trabajos_terreno/form_entries.db` (`|| echo` para tolerar "sin cambios").
7. `git push` de la base actualizada.
8. Subida de la base como artefacto (`if: always()`), como respaldo histórico por corrida.

> Nota: el comentario del cron en el archivo indica "lunes a viernes", pero la expresión
> `1-6` cubre de lunes a sábado. El comportamiento real es de lunes a sábado.

## 5. Consideraciones operativas

- **Ventana de procesamiento**: solo las últimas 100 submissions son visibles por
  ejecución. Si se acumulan más de 100 OT entre corridas, las más antiguas podrían quedar
  fuera de la ventana antes de ser procesadas.
- **Persistencia de la deduplicación**: la base SQLite se versiona; un conflicto de merge
  o un reset accidental sobre `form_entries.db` puede causar reprocesamiento.
- **Fallo de carga tras inserción en DB**: si la carga a SharePoint falla después de que
  `check_new_sub` insertó los IDs, esas OT no se reintentan en el job automático; deben
  reenviarse con `main_practice.py`.
- **Secreto rotado**: ante errores 401/403 de Graph o Connecteam, verificar la vigencia de
  `MS_CLIENT_SECRET` y `CONNECTEAM_API_KEY`.
