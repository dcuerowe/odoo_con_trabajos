import pandas as pd

df = pd.read_excel('reasignacion_st_detallada.xlsx')
revisar_df = df[df['Tipo de trabajo nuevo'] == 'Revisar']

print("Checking 'Revisar' for 'preventivo':")
for index, row in revisar_df.iterrows():
    causa = str(row['Causa visita'])
    if 'preventivo' in causa.lower():
        print(f"Row {index}: '{causa}' (Type: {type(row['Causa visita'])})")
        # Print hex to see hidden characters
        print(f"Hex: {causa.encode('utf-8').hex()}")
        break
else:
    print("No 'preventivo' found in Revisar rows.")
