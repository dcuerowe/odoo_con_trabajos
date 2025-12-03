import pandas as pd

file_path = 'resumen_trabajos.xlsx'
try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    # Print first row as dict to see values paired with columns
    if not df.empty:
        print("\nFirst row sample:")
        print(df.iloc[0].to_dict())
except Exception as e:
    print(f"Error reading file: {e}")
