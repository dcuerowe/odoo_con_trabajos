import pandas as pd
import unicodedata

# Load data
orig_file = 'resumen_trabajos.xlsx'
reclass_file = 'reasignacion_st_detallada.xlsx'

df_orig = pd.read_excel(orig_file)
df_orig.columns = [c.strip() for c in df_orig.columns]

df_reclass = pd.read_excel(reclass_file)

# 1. Extract Original 'I' records
df_i_orig = df_orig[df_orig['Tipo de trabajo'] == 'I'].copy()
df_i_orig['Origen'] = 'Original'

# 2. Extract Reclassified 'I' records
# The reclass file has columns: OT, Técnico, Proyecto, Asset, Tipo de trabajo anterior, Tipo de trabajo nuevo, Causa visita
# We need to fetch 'Resolución visita' and 'Observaciones' from the original dataframe to have full context.
# We can merge df_reclass with df_orig.
# Since df_reclass was a subset of df_orig where Tipo de trabajo == 'ST', we can try to match rows.
# However, OT is not unique.
# A safer approach:
# Take df_orig where Tipo de trabajo == 'ST'.
# Assign the 'Tipo de trabajo nuevo' from df_reclass (assuming order is preserved as in previous steps).
# Then filter for 'I'.

df_st_orig = df_orig[df_orig['Tipo de trabajo'] == 'ST'].copy()

# Verify lengths match
if len(df_st_orig) != len(df_reclass):
    print(f"Warning: Length mismatch! Original ST: {len(df_st_orig)}, Reclass: {len(df_reclass)}")
    # Fallback: Merge on index if possible, or trust the order if we are sure.
    # Given the previous execution flow, order should be preserved.
    # Let's assume order is preserved.
    df_st_orig['Tipo de trabajo nuevo'] = df_reclass['Tipo de trabajo nuevo'].values
else:
    df_st_orig['Tipo de trabajo nuevo'] = df_reclass['Tipo de trabajo nuevo'].values

df_i_reclass = df_st_orig[df_st_orig['Tipo de trabajo nuevo'] == 'I'].copy()
df_i_reclass['Origen'] = 'Reasignado ST'

# Combine both
df_installations = pd.concat([df_i_orig, df_i_reclass], ignore_index=True)

print(f"Total Installation records to analyze: {len(df_installations)}")

# Normalization function
def normalize_text(text):
    if pd.isna(text):
        return ""
    s = str(text).lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# Classification Logic
def subclassify_installation(row):
    text = normalize_text(f"{row['Causa visita']} {row['Resolución visita']} {row['Observaciones']}")
    causa = normalize_text(row['Causa visita'])
    
    # Keywords
    # Montaje: Physical work
    kw_montaje = ['montaje', 'instalacion fisica', 'canalizacion', 'soporte', 'fijacion', 'cableado', 'obra', 'civil', 'gabinete', 'tablero', 'sensor', 'sonda', 'equipo', 'instalacion']
    
    # Habilitación: Configuration, commissioning, logical work
    kw_habilitacion = ['configuracion', 'programacion', 'integracion', 'puesta en marcha', 'habilitacion', 'pruebas', 'validacion', 'conexion', 'sutron', 'telemetria', 'transmision', 'variables', 'lectura']
    
    # Logic
    # If it explicitly mentions configuration/integration as the MAIN cause or resolution without heavy physical work keywords, it's Habilitación.
    # However, "Instalación" often implies mounting.
    
    # Let's look for specific "Habilitación" triggers first.
    if any(k in causa for k in ['configuracion', 'programacion', 'integracion', 'conexion']):
        # Check if it also has heavy mounting words.
        # If it says "Instalación y configuración", it's a mix.
        # The user wants to know if it corresponds to Mounting OR Commissioning.
        # Usually, if it involves mounting, that's the dominant effort.
        # But if it's just "Conexión y configuración", it's Habilitación.
        if 'montaje' in text or 'canalizacion' in text or 'soporte' in text:
             return 'Montaje' # Physical work dominates
        return 'Habilitación'
        
    # If it says "Instalación", it's likely Montaje.
    if 'instalacion' in causa:
        return 'Montaje'
        
    # Check resolution for clues
    if any(k in text for k in ['configuracion', 'programacion', 'integracion', 'transmision']):
         if 'montaje' not in text and 'instalacion' not in text:
             return 'Habilitación'

    # Default to Montaje for "Instalación" category if unsure, as it implies physical presence.
    return 'Montaje'

df_installations['Sub-categoría'] = df_installations.apply(subclassify_installation, axis=1)

# Export
output_file = 'output/subclasificacion_instalaciones.xlsx'
df_installations.to_excel(output_file, index=False)
print(f"Results saved to {output_file}")

# Summary
print("\n--- Summary of Sub-classification ---")
print(df_installations['Sub-categoría'].value_counts())
print("\n--- Breakdown by Origin ---")
print(df_installations.groupby(['Origen', 'Sub-categoría']).size())
