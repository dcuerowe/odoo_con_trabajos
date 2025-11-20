import pandas as pd

file_path = 'odoo_con_trabajos/resumen_trabajos.xlsx'

try:
    df = pd.read_excel(file_path)
    
    # Columns of interest
    type_col = 'Tipo de trabajo'
    desc_col = 'Resolución visita'
    obs_col = 'Observaciones'
    cause_col = 'Causa visita'
    
    # Group by Job Type
    grouped = df.groupby(type_col)
    
    print(f"Total records: {len(df)}")
    print("-" * 40)
    
    for name, group in grouped:
        print(f"JOB TYPE: {name}")
        print(f"Count: {len(group)}")
        
        # Get most common causes
        print("Top Causes:")
        print(group[cause_col].value_counts().head(3).to_string())
        
        # Get a sample of descriptions (non-empty)
        descriptions = group[desc_col].dropna().unique()
        print(f"\nSample Descriptions ({min(5, len(descriptions))} of {len(descriptions)}):")
        for desc in descriptions[:5]:
            print(f"- {desc[:200]}...") # Truncate long descriptions
            
        print("\n" + "="*40 + "\n")

except Exception as e:
    print(f"Error analyzing file: {e}")
