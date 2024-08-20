import pandas as pd
import numpy as np

allSeniorPatients = pd.read_csv('allSeniorPatients.csv')
allPatientCurrent = pd.read_csv('allPatientCurrent.csv')

allSeniorPatients = allSeniorPatients[['First Name', 'Last Name', 'Record Id', 'DOB', 'Email', 'Mobile Phone']].copy()
allSeniorPatients.columns = ['First Name', 'Last Name', 'Record Id', 'DOB', 'Email', 'Mobile Phone']

allPatientCurrent = allPatientCurrent[allPatientCurrent['Age'] > 64]
allPatientCurrent = allPatientCurrent[['Record Id', 'Last Visit Date']].copy()
allPatientCurrent.columns = ['Record Id', 'Last Visited']

allSeniorPatients = pd.merge(allSeniorPatients, allPatientCurrent, on='Record Id', how='left')

allSeniorPatients['Last Visited'] = pd.to_datetime(allSeniorPatients['Last Visited'], errors='coerce')

mask_2023_2024 = allSeniorPatients['Last Visited'].dt.year.isin([2023, 2024])
mask_2022 = allSeniorPatients['Last Visited'].dt.year == 2022
mask_2021 = allSeniorPatients['Last Visited'].dt.year == 2021
mask_before_2021 = allSeniorPatients['Last Visited'].dt.year < 2021
mask_nan = allSeniorPatients['Last Visited'].isna()

allSeniorPatients[mask_2023_2024].to_csv('allSeniorPatients_2023_2024.csv', index=False)
allSeniorPatients[mask_2022].to_csv('allSeniorPatients_2022.csv', index=False)
allSeniorPatients[mask_2021].to_csv('allSeniorPatients_2021.csv', index=False)
allSeniorPatients[mask_before_2021].to_csv('allSeniorPatients_before_2021.csv', index=False)
allSeniorPatients[mask_nan].to_csv('allSeniorPatients_nan.csv', index=False)
