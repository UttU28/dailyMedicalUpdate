import pandas as pd
import re

def split_on_first_integer(text):
    match = re.search(r'\d+', text)
    if match:
        pos = match.start()
        return text[:pos].strip()
    else:
        return text.strip()

all_dataframes = []

for i in range(1, 6):
    allPrescriptions1 = pd.read_csv(f'prescriptionData/MedQ{i}.csv', on_bad_lines='skip')
    allPrescriptions1 = allPrescriptions1[['Drug Details']].copy()
    allPrescriptions1.columns = ['Drug Name']
    allPrescriptions1 = allPrescriptions1.drop_duplicates()
    allPrescriptions1['Drug Name'] = allPrescriptions1['Drug Name'].apply(split_on_first_integer)
    all_dataframes.append(allPrescriptions1)

combined_df = pd.concat(all_dataframes, ignore_index=True)
combined_df = combined_df.drop_duplicates()
combined_df.to_csv('prescriptionData/CombinedPrescriptions.csv', index=False)

print("Data combined and saved to 'prescriptionData/CombinedPrescriptions.csv'")
