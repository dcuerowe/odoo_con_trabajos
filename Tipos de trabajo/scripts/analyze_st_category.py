import pandas as pd

file_path = 'resumen_trabajos.xlsx'
df = pd.read_excel(file_path)
df.columns = [c.strip() for c in df.columns]

# Filter for ST
st_df = df[df['Tipo de trabajo'] == 'ST']

print(f"Total ST records: {len(st_df)}")

# Analyze 'Causa visita' frequencies
print("\n--- Causa visita frequencies in ST ---")
print(st_df['Causa visita'].value_counts().to_string())

# Let's look at 'Resolución visita' for the top causes to see if they match the cause description
top_causes = st_df['Causa visita'].value_counts().head(10).index.tolist()

for cause in top_causes:
    print(f"\n--- Samples for Causa: {cause} ---")
    subset = st_df[st_df['Causa visita'] == cause]
    # Print first 5 resolutions
    resolutions = subset['Resolución visita'].dropna().unique()[:5]
    for r in resolutions:
        print(f"  - {r}")
