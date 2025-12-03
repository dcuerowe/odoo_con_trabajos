import pandas as pd

df = pd.read_excel('reasignacion_st_detallada.xlsx')
revisar_df = df[df['Tipo de trabajo nuevo'] == 'Revisar']

print("Top 20 'Revisar' Causa visita:")
print(revisar_df['Causa visita'].value_counts().head(20).to_string())

print("\nSample 'Revisar' rows (Causa + Tipo original):")
print(revisar_df[['Causa visita', 'Tipo de trabajo anterior']].head(10).to_string())
