import pandas as pd

df = pd.read_csv('foll.csv')
filteredDF = df[df['Age'] >= 65]
# filteredDF.to_csv('filtered_file.csv', index=False)

newDF = filteredDF[['First Name', 'Last Name', 'Record Id', 'DOB', 'Email', 'Mobile Phone', 'Last Visit Date']].copy()
newDF.columns = ['First Name', 'Last Name', 'Record ID', 'DOB', 'Email', 'Mobile Phone', 'Last Visit Date']
newDF.to_csv('SeniorsNotVisited24M.csv', index=False)
