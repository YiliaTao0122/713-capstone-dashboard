import streamlit as st
import pandas as pd
import plotly.express as px

# Title and Introduction
st.title("EcoSoil Insights: Auckland Soil Quality Monitoring Dashboard")
st.markdown("""
This dashboard provides insights into Auckland's soil quality, integrating key metrics like pH, Total Carbon (TC%), Total Nitrogen (TN%), and trace elements 
(As, Cd, Cr, Cu, Ni, Pb, Zn). It aims to assist landowners, policymakers, and stakeholders in making data-driven decisions for sustainable land management.
""")

# File Upload
uploaded_file = st.file_uploader("Upload your cleaned dataset (CSV)", type=["csv"])

if uploaded_file:
    # Load data
    data = pd.read_csv(uploaded_file)

    # Sidebar Filters
    st.sidebar.title("Filters")
    land_use_filter = st.sidebar.multiselect("Select Land Use", data['Land use'].unique())
    period_filter = st.sidebar.multiselect("Select Period", data['Period'].unique())
    site_filter = st.sidebar.multiselect("Select Site", data['Site No.1'].unique())

    # Filter data
    filtered_data = data
    if land_use_filter:
        filtered_data = filtered_data[filtered_data['Land use'].isin(land_use_filter)]
    if period_filter:
        filtered_data = filtered_data[filtered_data['Period'].isin(period_filter)]
    if site_filter:
        filtered_data = filtered_data[filtered_data['Site No.1'].isin(site_filter)]

    # Key Performance Indicators (KPIs)
    st.header("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average pH", round(filtered_data['pH'].mean(), 2))
    col2.metric("Average Olsen P (mg/kg)", round(filtered_data['Olsen P'].mean(), 2))
    col3.metric("Average Bulk Density (g/cm³)", round(filtered_data['BD'].mean(), 2))

    # Contamination Levels
    st.header("Contamination Levels")
    if 'ICI_Class' in filtered_data.columns:
        contamination_fig = px.pie(filtered_data, names='ICI_Class', title="Contamination Levels Distribution")
        st.plotly_chart(contamination_fig)

    # Soil Metric Trends
    st.header("Soil Metric Trends Over Time")
    metric_options = ['pH', 'TC %', 'TN %', 'Olsen P', 'AMN', 'BD']
    selected_metric = st.selectbox("Select a metric to view trends", metric_options)
    if 'Year' in filtered_data.columns:
        trend_fig = px.line(filtered_data, x='Year', y=selected_metric, color='Land use', title=f"{selected_metric} Trends Over Time")
        st.plotly_chart(trend_fig)

    # Geographic Distribution
    st.header("Geographical Distribution of Monitoring Sites")
    if 'Latitude' in filtered_data.columns and 'Longitude' in filtered_data.columns:
        map_fig = px.scatter_mapbox(
            filtered_data,
            lat='Latitude',
            lon='Longitude',
            color='ICI_Class',
            size='Olsen P',
            hover_name='Site No.1',
            title="Soil Monitoring Sites",
            mapbox_style="open-street-map"
        )
        st.plotly_chart(map_fig)

    # Trace Elements
    st.header("Trace Element Analysis")
    trace_elements = ['As', 'Cd', 'Cr', 'Cu', 'Ni', 'Pb', 'Zn']
    selected_trace = st.selectbox("Select a trace element to view details", trace_elements)
    trace_fig = px.box(filtered_data, x='Land use', y=selected_trace, color='Land use', title=f"{selected_trace} Levels by Land Use")
    st.plotly_chart(trace_fig)

    # Recommendations
    st.header("Recommendations")
    st.markdown("""
    - **High Olsen P Sites**: Reduce phosphate fertilizer usage and adopt slow-release alternatives.
    - **Low Macroporosity Sites**: Minimize heavy stocking during wet periods to prevent compaction.
    - **High Contamination Sites**: Monitor and remediate trace element contamination to meet guidelines.
    """)

    # Data Download
    st.header("Download Filtered Data")
    filtered_csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_csv,
        file_name="filtered_soil_data.csv",
        mime="text/csv",
    )
else:
    st.info("Please upload a CSV file to view the dashboard.")


