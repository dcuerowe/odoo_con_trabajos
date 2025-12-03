import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata

# Load data
file_path = 'resumen_trabajos.xlsx'
df = pd.read_excel(file_path)
df.columns = [c.strip() for c in df.columns]

# Filter ST
st_df = df[df['Tipo de trabajo'] == 'ST'].copy()

def normalize_text(text):
    if pd.isna(text):
        return ""
    # Normalize unicode characters to decompose combined characters (like ñ or accents)
    # Then encode to ASCII ignoring errors to strip accents
    s = str(text).lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# Define classification logic
def classify_row(row):
    # Normalize all inputs to remove accents
    causa = normalize_text(row['Causa visita'])
    resolucion = normalize_text(row['Resolución visita'])
    obs = normalize_text(row['Observaciones'])
    
    text = f"{causa} {resolucion} {obs}"
    
    # Logic hierarchy (Order matters!)
    
    # 1. Solicitud Operativa
    if any(k in text for k in ['toma de fotogra', 'foto', 'aumento de caudal', 'disminucion de caudal', 'apoyo', 'acompanamiento', 'entrega de', 'visita a terreno', 'capacitacion', 'reunion']):
        return 'SO'
        
    # 2. Mantenimiento Preventivo
    if any(k in causa for k in ['preventivo', 'mantencion', 'limpieza', 'contrastacion', 'calibracion', 'verificacion']):
        return 'MP'
    if 'mantenimiento' in causa and 'correctivo' not in causa:
        return 'MP'
        
    # 3. Instalación
    if any(k in causa for k in ['instalacion', 'montaje', 'habilitacion', 'integracion', 'mejoramiento', 'implementacion', 'nuevo punto']):
        return 'I'
        
    # 4. Configuración
    if any(k in causa for k in ['configuracion', 'programacion', 'ajuste', 'firmware', 'parametro', 'rango', 'setpoint']):
        return 'CF'
    if any(k in text for k in ['configuracion', 'programacion', 'actualizacion de firmware']):
        return 'CF'

    # 5. Mantenimiento Correctivo
    if any(k in text for k in ['correctivo', 'falla', 'reparacion', 'cambio', 'reinicio', 'error', 'defectuoso', 'danado', 'quemado', 'sin comunicacion', 'recuperacion', 'reemplazo', 'sin datos', 'no transmite']):
        return 'MC'
    if 'revision' in causa or 'soporte' in causa:
        return 'MC'
    
    # 6. Levantamiento
    if any(k in text for k in ['levantamiento', 'inspeccion', 'diagnostico', 'inventario']):
        return 'LT'
        
    # Default fallback
    return 'Revisar'

# Apply classification
st_df['Tipo de trabajo nuevo'] = st_df.apply(classify_row, axis=1)

# Prepare detailed dataframe
output_columns = ['OT', 'Técnico', 'Proyecto', 'Asset', 'Tipo de trabajo', 'Tipo de trabajo nuevo', 'Causa visita']
detailed_df = st_df[output_columns].rename(columns={'Tipo de trabajo': 'Tipo de trabajo anterior'})

# Save to Excel
output_file = 'reasignacion_st_detallada.xlsx'
detailed_df.to_excel(output_file, index=False)
print(f"Detailed reclassification saved to {output_file}")

# Generate Summary Chart
plt.figure(figsize=(10, 6))
counts = detailed_df['Tipo de trabajo nuevo'].value_counts()
sns.barplot(x=counts.index, y=counts.values, hue=counts.index, legend=False, palette='viridis')
plt.title('Redistribución de Registros ST (Soporte Técnico)')
plt.xlabel('Nueva Categoría Asignada')
plt.ylabel('Cantidad de Registros')
plt.bar_label(plt.gca().containers[0])

# Save chart
chart_file = 'distribucion_reasignacion_st.png'
plt.savefig(chart_file)
print(f"Chart saved to {chart_file}")

# Print summary for context
print("\nSummary of Reclassification:")
print(counts)
