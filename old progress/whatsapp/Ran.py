#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

# Load the dataset
file_path = "clean_congress_bills_data (1).csv"  
df = pd.read_csv(file_path)

# Select only numerical columns
numeric_df = df.select_dtypes(include=['number'])

# Compute the variance of each numerical feature
variances = numeric_df.var()

# Define a threshold to identify low-variance features (e.g., 0.01)
threshold = 0.01
low_variance_features = variances[variances < threshold].index

# Remove features with variance below the threshold
filtered_df = df.drop(columns=low_variance_features)

# Print the number of removed features and the number of remaining features
print(f"Removed {len(low_variance_features)} low-variance features, {filtered_df.shape[1]} features remain.")

# Save the cleaned dataset (optional)
filtered_df.to_csv("filtered_congress_bills_data.csv", index=False)


# In[2]:


import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold

# Load the dataset
file_path = "clean_congress_bills_data (1).csv"  
df = pd.read_csv(file_path)

# Select numerical features
num_features = df.select_dtypes(include=[np.number]).columns

# Compute variance for all numerical features
variance = df[num_features].var()
print("Variance of numerical features:")
print(variance)

# Set a variance threshold (e.g., 0.01)
vt = VarianceThreshold(threshold=0.01)

# Fill missing values with 0 temporarily for variance calculation
X_num = df[num_features].fillna(0)

# Fit the VarianceThreshold selector
vt.fit(X_num)

# Get features to keep (above the variance threshold)
features_to_keep = X_num.columns[vt.get_support()]

print("\nNumerical features to keep (variance above threshold):")
print(list(features_to_keep))

# Identify features to drop
features_to_drop = set(num_features) - set(features_to_keep)
print("\nDropping features:", features_to_drop)

# Drop the near-zero variance features
df_filtered = df.drop(columns=list(features_to_drop))

# Save the cleaned dataset (optional)
df_filtered.to_csv("filtered_congress_bills_data.csv", index=False)


# In[ ]:




