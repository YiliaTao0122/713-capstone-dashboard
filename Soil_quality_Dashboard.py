import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Title and Introduction
st.title("EcoSoil Insights: Auckland Soil Quality Monitoring Dashboard")
st.markdown("""
This interactive dashboard provides key insights into Auckland's soil quality, empowering landowners, policymakers, and agricultural practitioners 
to make data-driven decisions for sustainable land management.
""")

# File Upload
uploaded_file = st.file_uploader("Upload your cleaned dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    # Ensure 'Year' column is present and sorted
    if 'Year' in data.columns:
        data = data.sort_values(by='Year')
        data.set_index('Year', inplace=True)

    # Sidebar Filters
    st.sidebar.title("Filters")
    land_use_filter = st.sidebar.multiselect("Select Land Use", data['Land use'].unique()) if 'Land use' in data.columns else None
    period_filter = st.sidebar.multiselect("Select Period", data['Period'].unique()) if 'Period' in data.columns else None
    site_filter = st.sidebar.multiselect("Select Site Number", data['Site Num'].unique()) if 'Site Num' in data.columns else None

    # Filter data
    filtered_data = data
    if land_use_filter:
        filtered_data = filtered_data[filtered_data['Land use'].isin(land_use_filter)]
    if period_filter:
        filtered_data = filtered_data[filtered_data['Period'].isin(period_filter)]
    if site_filter:
        filtered_data = filtered_data[filtered_data['Site Num'].isin(site_filter)]

    # Display Selected Filters in Sidebar
    st.sidebar.header("Selected Filters")
    st.sidebar.write(f"Land Use: {', '.join(land_use_filter) if land_use_filter else 'All'}")
    st.sidebar.write(f"Period: {', '.join(period_filter) if period_filter else 'All'}")
    st.sidebar.write(f"Site Number: {', '.join(map(str, site_filter)) if site_filter else 'All'}")

    # Right-Side Summary Display
    st.header("Filter Results Summary")
    if not filtered_data.empty:
        st.write("### Details of Filtered Data:")
        st.write(f"**Land Use:** {filtered_data['Land use'].unique()}")
        st.write(f"**Soil Series:** {filtered_data['Soil series'].unique()}")
        st.write(f"**Soil Texture:** {filtered_data['Soil texture'].unique()}")
        st.write(f"**Soil Type:** {filtered_data['Soil type'].unique()}")
        st.write(f"**Soil Classification:** {filtered_data['Soil classification'].unique()}")
    else:
        st.warning("No data available for the selected filters.")

    # Contamination Analysis with ICI
    st.header("Contamination Analysis")
    if 'ICI' in filtered_data.columns:
        filtered_data['ICI_Class'] = filtered_data['ICI'].apply(
            lambda x: "Low" if x < 1 else ("Moderate" if x <= 3 else "High")
        )
        # Define color map
        color_map = {"Low": "green", "Moderate": "yellow", "High": "red"}
        fig = px.scatter(
            filtered_data,
            x="Site Num",
            y="ICI",
            color="ICI_Class",
            color_discrete_map=color_map,
            title="ICI Levels with Classification",
            labels={"ICI": "Integrated Contamination Index (ICI)"}
        )
        st.plotly_chart(fig)

        # Recommendations
        st.subheader("ICI Recommendations")
        st.write("- **Low (Green):** Maintain current soil management practices.")
        st.write("- **Moderate (Yellow):** Reduce contaminant inputs and consider enhancement strategies.")
        st.write("- **High (Red):** Immediate remediation required. Consult soil management experts.")
    else:
        st.warning("ICI data not available in the uploaded dataset.")
