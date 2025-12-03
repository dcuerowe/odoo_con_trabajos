import pandas as pd
import json

# Load original data
df_orig = pd.read_excel('resumen_trabajos.xlsx')
df_orig.columns = [c.strip() for c in df_orig.columns]

# Load reclassified ST data
df_reclass = pd.read_excel('output/reasignacion_st_detallada.xlsx')

# Prepare datasets to merge
# 1. Non-ST from original
df_non_st = df_orig[df_orig['Tipo de trabajo'] != 'ST'].copy()

# 2. Reclassified ST
# We need to make sure columns match for concatenation
# df_reclass has: OT, Técnico, Proyecto, Asset, Tipo de trabajo anterior, Tipo de trabajo nuevo, Causa visita
# We need to bring back 'Resolución visita' and 'Observaciones' from original for context
# Let's join df_reclass with df_orig on index or OT to get full details.
# Assuming df_reclass was created from df_orig['Tipo de trabajo'] == 'ST' preserving index?
# Let's assume index is preserved or we can merge on OT + Technician + Causa? 
# OT might not be unique.
# Let's rely on the fact that I created the reclass file from the filtered dataframe.
# To be safe, let's just use the original dataframe and update the ST rows.

df_final = df_orig.copy()
st_indices = df_final[df_final['Tipo de trabajo'] == 'ST'].index

# We need to map the new types back. 
# The reclass file might not have the original index explicitly saved as a column, 
# but it was generated from the ST subset.
# Let's assume the order is the same.
if len(st_indices) == len(df_reclass):
    df_final.loc[st_indices, 'Tipo de trabajo'] = df_reclass['Tipo de trabajo nuevo'].values
else:
    print("Warning: Length mismatch. Fallback to merge logic if needed.")

# Define categories to sample
categories = ['MP', 'MC', 'I', 'LT', 'C', 'G', 'SO', 'CF']

samples = {}

for cat in categories:
    # Filter
    subset = df_final[df_final['Tipo de trabajo'] == cat]
    
    # Take up to 10 samples
    # We prefer samples that have non-null Asset if possible, and good descriptions
    subset_valid = subset.dropna(subset=['Causa visita', 'Resolución visita'])
    if len(subset_valid) < 10:
        subset_valid = subset # Fallback
        
    sample_rows = subset_valid.head(10)
    
    cat_samples = []
    for _, row in sample_rows.iterrows():
        cat_samples.append({
            'OT': row['OT'],
            'Técnico': row['Técnico'],
            'Asset': row['Asset'],
            'Causa': row['Causa visita'],
            'Resolución': row['Resolución visita']
        })
    samples[cat] = cat_samples

print(json.dumps(samples, indent=2, ensure_ascii=False))
