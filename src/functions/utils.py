import pandas as pd

def split_date(data_df, date_column):
    # Ensure 'Date' column is in datetime format
    data_df[date_column] = pd.to_datetime(data_df[date_column])
    data_df['weekday'] = data_df[date_column].dt.weekday
    data_df['month'] = data_df[date_column].dt.month
    data_df['hour'] = data_df[date_column].dt.hour
    data_df[date_column] = data_df[date_column].dt.date
    data_df = data_df.sort_values(by=date_column)

    return data_df
