import plotly.express as px
import streamlit as st
import pandas as pd

from functions.charts import gauge, line_chart
from functions.model import load_model, load_feature_columns_from_json
from functions.utils import split_date


# Function to manually input data
def manual_data_input(data_method):
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()

    # Get input data
    aqi = st.number_input("Enter Air Quality Index", min_value=0, max_value=999)
    date = st.date_input("Enter Date")
    category = st.selectbox("Select the Air Quality Category:", ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "SLIGHT"])
    pollutant = st.selectbox("Select the Pollutant:", ["PM2.5", "Ozone 8-hr", "Carbon monoxide", "PM10", "Oz", "Ozone 1-hr"])
    pollen_type = st.selectbox("Select the Pollen Type:",
                               ["Grass", "Ragweed", "Cedar", "Elm", "Alder", "Juniper", "Birch", "Maple", "Hickory", "Oak", "Pine", "Mulberry",
                                "Goldenrod", "Poplar", "Ash", "Hackberry"])
    pollen_description = st.selectbox("Select the Pollen Description:",
                                      ["Not on file", "Slight", " Maple", " Ragweed", " Grass", " Juniper", "Moderate", " Mulberry", " Cedar",
                                       " Pine", " Poplar", " Oak", " Sweet Gum", "Heavy", " Elm", "Extremely Heavy", " Walnut", " Alder", " Birch",
                                       " Hickory",
                                       " Hackberry"])

    row = pd.DataFrame({'AQI': [aqi], 'Date': [date], 'Category': [category], 'Pollutant': [pollutant],
                        'Pollen Type': [pollen_type], 'PollenDescription': [pollen_description]})

    if data_method == 'Visualization':
        pollen_level = st.number_input("Enter Pollen Concentration", min_value=0.0)
        row['Pollen Concentration'] = [pollen_level]

    if st.button("Add Data"):
        st.session_state.df = pd.concat([st.session_state.df, row], ignore_index=True)
        st.write("Current Data:")
        st.write(st.session_state.df)

    return st.session_state.df


# Function to load CSV data
def load_csv_file():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return pd.DataFrame()


# Function to display alerts based on pollen levels
def threshold_validation(value, threshold):
    if value > threshold:
        text = "Alert! High pollen concentration detected."
    else:
        text = "The pollen concentration is within safe limits."

    return text


def vizualization_method(data_df, threshold, date_column='Date', pollen_column='Pollen Concentration'):
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        data_df = pd.read_csv(uploaded_file)
        st.write("Data from CSV:")
        st.write(data_df)

        # Allow user to select columns for data fields
        st.subheader("Select Data Columns")
        date_column = st.selectbox("Select Columns for Data", options=data_df.columns.tolist())
        pollen_column = st.selectbox("Select Column for Pollen Concentration", options=data_df.columns.tolist())

    if st.button("Process Data"):

        data_df = split_date(data_df, date_column)

        data_df = data_df[[date_column, pollen_column]].dropna()

        # Check if data_df has more than one row
        if len(data_df) > 1:
            fig = line_chart(data_df, date_column, pollen_column, threshold)

            # Show the chart
            st.plotly_chart(fig)
        else:
            threshold_text = threshold_validation(data_df[pollen_column].iloc[0], threshold)
            fig = gauge(data_df[pollen_column].iloc[0], threshold_text, threshold)

            # Show the chart
            st.plotly_chart(fig)


def prediction_method(model, feature_columns, threshold, date_column='Date', pollen_column='Pollen Concentration'):
    if st.button("Process Data"):
        df_to_predict = st.session_state.df
        df_to_predict = split_date(df_to_predict, date_column)

        # Encode categorical variables
        df_encoded = pd.get_dummies(df_to_predict)

        # Reindex to ensure all columns required by the model
        df_encoded = df_encoded.reindex(columns=feature_columns, fill_value=False)

        # Make predictions for all rows
        pollen_levels = model.predict(df_encoded)

        # Add the prediction column to the original DataFrame
        st.session_state.df[pollen_column] = pollen_levels

        # Reorder columns to move the pollen column to the first position
        cols = [pollen_column] + [col for col in st.session_state.df.columns if col != pollen_column]

        st.session_state.df = st.session_state.df[cols]

        # Check if data_df has more than one row
        if len(df_to_predict) > 1:
            fig = line_chart(df_to_predict, date_column, pollen_column, threshold)

            # Show the chart
            st.plotly_chart(fig)
        else:
            threshold_text = threshold_validation(st.session_state.df[pollen_column].iloc[0], threshold)
            fig = gauge(st.session_state.df[pollen_column].iloc[0], threshold_text, threshold)

            # Show the chart
            st.plotly_chart(fig)


# Main function to display charts and interface
def main():
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()

    model = load_model("../models/random_forest.joblib")
    feature_columns = load_feature_columns_from_json('../feature_columns.json')
    st.title("Pollen Concentration Prediction & Alert System")

    # Option to choose manual input or CSV upload
    data_method = st.radio("Choose The Data Method", ("Visualization", "Prediction"))
    threshold = st.slider("Set Pollen Alert Threshold", 0, 100, 50)

    # Call the manual input function to handle user inputs and update df
    data_df = manual_data_input(data_method)

    if data_method == "Visualization":
        vizualization_method(data_df, threshold)

    elif data_method == 'Prediction':
        prediction_method(model, feature_columns, threshold)


if __name__ == "__main__":
    main()
