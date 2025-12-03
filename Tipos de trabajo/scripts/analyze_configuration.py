import pandas as pd

file_path = 'resumen_trabajos.xlsx'
df = pd.read_excel(file_path)
df.columns = [c.strip() for c in df.columns]

# Keywords related to configuration
keywords = ['configur', 'program', 'ajuste', 'parametro', 'setpoint', 'calibracion', 'rango']

# Function to check if any keyword is in the text
def has_keyword(text):
    if pd.isna(text):
        return False
    text = str(text).lower()
    return any(k in text for k in keywords)

# Filter rows where 'Causa visita', 'Resolución visita' or 'Observaciones' contain keywords
config_df = df[
    df['Causa visita'].apply(has_keyword) | 
    df['Resolución visita'].apply(has_keyword) |
    df['Observaciones'].apply(has_keyword)
]

print(f"Total records with configuration keywords: {len(config_df)}")
print("\n--- Distribution by Current 'Tipo de trabajo' ---")
print(config_df['Tipo de trabajo'].value_counts().to_string())

print("\n--- Sample Records (Causa vs Resolución) ---")
# Show a mix of categories to see context
for category in config_df['Tipo de trabajo'].unique():
    print(f"\nCategory: {category}")
    sample = config_df[config_df['Tipo de trabajo'] == category].head(5)
    for index, row in sample.iterrows():
        print(f"  Causa: {row['Causa visita']}")
        print(f"  Resolución: {str(row['Resolución visita'])[:150]}...") # Truncate for readability
        print("-" * 20)
