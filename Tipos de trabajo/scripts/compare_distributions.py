import pandas as pd
import matplotlib.pyplot as plt

# 1. Load Original Data
original_file = 'resumen_trabajos.xlsx'
df_orig = pd.read_excel(original_file)
df_orig.columns = [c.strip() for c in df_orig.columns]

# Get original counts
original_counts = df_orig['Tipo de trabajo'].value_counts()

# 2. Load Reclassification Data for ST
reclass_file = 'reasignacion_st_detallada.xlsx'
df_reclass = pd.read_excel(reclass_file)

# 3. Construct "New State" Data
# We start with the original types
new_types = df_orig['Tipo de trabajo'].copy()

# We need to map the reclassified STs back to the main list.
# Assuming the order hasn't changed, we can match by index if we are careful, 
# but it's safer to match by OT or just replace the ST block if we know they are the same subset.
# Since we filtered ST to create the reclass file, let's create a mapping dictionary from the reclass file.
# However, the reclass file might not have a unique ID per row if OTs are repeated. 
# Let's assume the reclass file corresponds exactly to the rows where Tipo de trabajo == 'ST'.

# Verify lengths
st_indices = df_orig[df_orig['Tipo de trabajo'] == 'ST'].index
if len(st_indices) != len(df_reclass):
    print(f"Warning: Original ST count ({len(st_indices)}) matches Reclass count ({len(df_reclass)})?")

# Update the new_types series
# We iterate through the reclass dataframe and update the corresponding index in new_types
# To do this robustly, we'll assume the reclass file was generated preserving the original index or order.
# In the previous script, we did: st_df = df[df['Tipo de trabajo'] == 'ST'].copy()
# So the order within the ST block should be preserved relative to the filtered block.

# Let's map the new values to the original indices
new_values_list = df_reclass['Tipo de trabajo nuevo'].tolist()

# Assign new values to the ST indices
new_types.loc[st_indices] = new_values_list

# Get new counts
new_counts = new_types.value_counts()

# 4. Generate Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Color map to ensure consistency if possible, or just let matplotlib handle it
# We can define a standard color palette
all_labels = set(original_counts.index) | set(new_counts.index)
colors = plt.cm.tab20.colors
color_map = {label: colors[i % len(colors)] for i, label in enumerate(all_labels)}

# Plot 1: Original
wedges1, texts1, autotexts1 = ax1.pie(
    original_counts, 
    labels=original_counts.index, 
    autopct='%1.1f%%', 
    startangle=140,
    colors=[color_map.get(x, 'gray') for x in original_counts.index],
    pctdistance=0.85
)
ax1.set_title('Distribución Original (Con ST)')

# Plot 2: New
wedges2, texts2, autotexts2 = ax2.pie(
    new_counts, 
    labels=new_counts.index, 
    autopct='%1.1f%%', 
    startangle=140,
    colors=[color_map.get(x, 'gray') for x in new_counts.index],
    pctdistance=0.85
)
ax2.set_title('Nueva Distribución (ST Reasignado)')

plt.tight_layout()
plt.savefig('comparacion_distribucion_categorias.png')
print("Comparison chart saved to comparacion_distribucion_categorias.png")

# Print text summary
print("\nOriginal Counts:")
print(original_counts)
print("\nNew Counts:")
print(new_counts)
