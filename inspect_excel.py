import pandas as pd
import os

file_path = 'odoo_con_trabajos/resumen_trabajos.xlsx'

try:
    df = pd.read_excel(file_path)
    print("Columns found:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())
    
except Exception as e:
    print(f"Error reading file: {e}")
