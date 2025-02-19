import pandas as pd

# load the original dataset
df = pd.read_csv("congress_118_bills.csv")

# fill missing values where necessary
df['Sponsor'].fillna('Unknown', inplace=True)
df['Committees'].fillna('None', inplace=True)
df['Vote Type'].fillna('No Vote', inplace=True)
df['Vote Date'].fillna('Unknown', inplace=True)
df['Vote Result'].fillna('No Result', inplace=True)
df['Related Bills'].fillna('None', inplace=True)

# extract introduced date from the raw text
df['Introduced'] = df['Introduced'].str.extract(r'([A-Za-z]+ \d{1,2}, \d{4})')
df['Introduced'] = pd.to_datetime(df['Introduced'], errors='coerce')

# convert vote date to datetime
df['Vote Date'] = pd.to_datetime(df['Vote Date'], errors='coerce')

# extract the main status without extra date info
df['Status Date'] = df['Status'].str.extract(r'\((.*?)\)')
df['Status Date'] = pd.to_datetime(df['Status Date'], errors='coerce')
df['Cleaned Status'] = df['Status'].str.extract(r'([A-Za-z ]+)')

# fix vote date for bills that are only 'Introduced'
df.loc[df['Cleaned Status'] == "Introduced", 'Vote Date'] = df['Introduced']

# clean up the 'Related Bills' column (remove leading/trailing commas)
df['Related Bills'] = df['Related Bills'].astype(str).str.strip(', ')

# feature engineering: count the number of cosponsors
df['Cosponsor Count'] = df['Cosponsor List'].apply(lambda x: len(x.split(',')) if isinstance(x, str) else 0)

# create a binary column for whether the bill has cosponsors
df['Has Cosponsors'] = df['Cosponsors (Overview)'].apply(lambda x: 1 if isinstance(x, str) and "Cosponsors" in x else 0)

# extract all unique subjects from the 'Subjects' column
unique_subjects = set()
df['Subjects'].dropna().apply(lambda x: unique_subjects.update(x.split(',')))

# create binary columns for each subject (1 if the bill contains the subject, 0 otherwise)
for subject in unique_subjects:
    df[subject.strip()] = df['Subjects'].apply(lambda x: 1 if subject in str(x) else 0)

# drop unnecessary columns
df.drop(columns=['Summary', 'Source URL', 'Cosponsors (Overview)', 'Cosponsor List', 'Status', 'Prognosis', 'Subjects'], inplace=True)

# save the final dataset
df.to_csv("final_congress_bills_dataset.csv", index=False)

