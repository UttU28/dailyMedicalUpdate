import pandas as pd
import re

# Function to split based on the first integer found
def split_on_first_integer(text):
    # Find the position of the first integer
    match = re.search(r'\d+', text)
    if match:
        pos = match.start()
        return text[:pos].strip()  # Return the part before the first integer
    else:
        return text.strip()  # Return the whole text if no integer is found

all_dataframes = []

for i in range(1, 6):
    # Read the CSV file
    allPrescriptions1 = pd.read_csv(f'prescriptionData/MedQ{i}.csv', on_bad_lines='skip')
    
    # Select the 'Drug Details' column
    allPrescriptions1 = allPrescriptions1[['Drug Details']].copy()
    
    # Rename the column
    allPrescriptions1.columns = ['Drug Name']
    
    # Remove duplicates
    allPrescriptions1 = allPrescriptions1.drop_duplicates()
    
    # Apply the splitting function
    allPrescriptions1['Drug Name'] = allPrescriptions1['Drug Name'].apply(split_on_first_integer)
    
    # Append to the list of dataframes
    all_dataframes.append(allPrescriptions1)

# Combine all dataframes
combined_df = pd.concat(all_dataframes, ignore_index=True)

# Remove duplicates in the combined dataframe
combined_df = combined_df.drop_duplicates()

# Save to a new CSV file
combined_df.to_csv('prescriptionData/CombinedPrescriptions.csv', index=False)

print("Data combined and saved to 'prescriptionData/CombinedPrescriptions.csv'")
