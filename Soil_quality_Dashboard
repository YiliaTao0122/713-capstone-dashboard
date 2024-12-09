import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Soil Quality Dashboard")
st.sidebar.title("Filters")

# Upload dataset
uploaded_file = st.file_uploader("Upload your cleaned dataset", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    
    # Sidebar Filters
    land_use_filter = st.sidebar.multiselect("Select Land Use", data['Land use'].unique())
    period_filter = st.sidebar.multiselect("Select Period", data['Period'].unique())

    # Filter data
    filtered_data = data
    if land_use_filter:
        filtered_data = filtered_data[filtered_data['Land use'].isin(land_use_filter)]
    if period_filter:
        filtered_data = filtered_data[filtered_data['Period'].isin(period_filter)]

    # KPIs
    st.metric("Average pH", round(filtered_data['pH'].mean(), 2))
    st.metric("Sites Monitored", filtered_data['Site No.1'].nunique())

    # Contamination Levels
    contamination_fig = px.pie(filtered_data, names='ICI_Class', title="Contamination Levels")
    st.plotly_chart(contamination_fig)

    # Trends
    trend_fig = px.line(filtered_data, x='Year', y='pH', color='Land use', title="pH Trends Over Time")
    st.plotly_chart(trend_fig)
