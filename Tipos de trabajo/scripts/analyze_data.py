import pandas as pd

file_path = 'resumen_trabajos.xlsx'
df = pd.read_excel(file_path)

# Normalize column names just in case
df.columns = [c.strip() for c in df.columns]

# Group by 'Tipo de trabajo'
grouped = df.groupby('Tipo de trabajo')

for name, group in grouped:
    print(f"--- TIPO DE TRABAJO: {name} ---")
    print(f"Total registros: {len(group)}")
    
    print("\nTop 5 Causa visita:")
    print(group['Causa visita'].value_counts().head(5).to_string())
    
    print("\nSample Resolución visita (5):")
    resoluciones = group['Resolución visita'].dropna().unique()
    for r in resoluciones[:5]:
        print(f"- {r}")
        
    print("\nSample Observaciones (5):")
    observaciones = group['Observaciones'].dropna().unique()
    for o in observaciones[:5]:
        print(f"- {o}")
    
    print("\n" + "="*40 + "\n")
