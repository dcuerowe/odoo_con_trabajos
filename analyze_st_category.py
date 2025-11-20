import pandas as pd
from collections import Counter
import re

file_path = 'odoo_con_trabajos/resumen_trabajos.xlsx'

try:
    df = pd.read_excel(file_path)
    
    # Filter for ST
    st_df = df[df['Tipo de trabajo'] == 'ST'].copy()
    
    print(f"Total ST records: {len(st_df)}")
    print("-" * 40)
    
    # Analyze 'Causa visita'
    print("Top 'Causa visita' in ST:")
    print(st_df['Causa visita'].value_counts().head(10).to_string())
    print("-" * 40)
    
    # Keyword analysis in 'Resolución visita'
    text_data = st_df['Resolución visita'].dropna().astype(str).tolist()
    all_text = " ".join(text_data).lower()
    
    # Simple keyword counting (excluding common stop words)
    words = re.findall(r'\w+', all_text)
    stop_words = {'de', 'la', 'el', 'en', 'y', 'a', 'se', 'que', 'del', 'por', 'con', 'los', 'para', 'las', 'un', 'una', 'su', 'al', 'lo', 'es', 'no'}
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    print("Top Keywords in Descriptions:")
    print(Counter(filtered_words).most_common(20))
    print("-" * 40)
    
    # Sample descriptions for specific keywords to understand context
    keywords_to_check = ['fuga', 'válvula', 'sensor', 'cambio', 'instalación', 'revisión', 'falla', 'bomba', 'tablero', 'comunicación']
    
    for kw in keywords_to_check:
        print(f"\n--- Samples for '{kw}' ---")
        samples = st_df[st_df['Resolución visita'].str.contains(kw, case=False, na=False)]['Resolución visita'].head(3).tolist()
        for s in samples:
            print(f"* {s[:150]}...")

except Exception as e:
    print(f"Error analyzing file: {e}")
