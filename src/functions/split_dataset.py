import pandas as pd

df = pd.read_csv('../../dataset/Air_Quality_and_Pollen_Count.csv')

# Randomly selecting 50 not na rows for validation set
df_non_na = df.dropna()
df_validation = df_non_na.sample(n=50, random_state=42)

# Creating train/test set by removing the selected validation rows
df_train_test = df.drop(df_validation.index)

# Saving the data sets
df_validation.to_csv('./dataset/Pollen_Concentration_validation.csv', index=False)
df_train_test.to_csv('./dataset/Pollen_Concentration_train_test.csv', index=False)
