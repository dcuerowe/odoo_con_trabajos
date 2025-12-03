import pandas as pd

file_path = 'resumen_trabajos.xlsx'
df = pd.read_excel(file_path)
df.columns = [c.strip() for c in df.columns]

st_df = df[df['Tipo de trabajo'] == 'ST']

# Print ALL Causa visita counts to see the long tail
print(st_df['Causa visita'].value_counts().to_string())
