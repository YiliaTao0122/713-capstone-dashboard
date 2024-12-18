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

    # Standardize column names
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Ensure 'year' column is present and sorted
    if 'year' in data.columns:
        data = data.sort_values(by='year')
        data.set_index('year', inplace=True)

    # Sidebar Filters
    st.sidebar.title("Filters")
    land_use_filter = st.sidebar.multiselect("Select Land Use", data['land_use'].unique()) if 'land_use' in data.columns else None
    period_filter = st.sidebar.multiselect("Select Period", data['period'].unique()) if 'period' in data.columns else None
    site_filter = st.sidebar.multiselect("Select Site Number", data['site_num'].unique()) if 'site_num' in data.columns else None

    # Filter data
    filtered_data = data
    if land_use_filter:
        filtered_data = filtered_data[filtered_data['land_use'].isin(land_use_filter)]
    if period_filter:
        filtered_data = filtered_data[filtered_data['period'].isin(period_filter)]
    if site_filter:
        filtered_data = filtered_data[filtered_data['site_num'].isin(site_filter)]

    # Display Selected Filters in Sidebar
    st.sidebar.header("Selected Filters")
    st.sidebar.write(f"Land Use: {', '.join(land_use_filter) if land_use_filter else 'All'}")
    st.sidebar.write(f"Period: {', '.join(period_filter) if period_filter else 'All'}")
    st.sidebar.write(f"Site Number: {', '.join(map(str, site_filter)) if site_filter else 'All'}")

    # Right-Side Summary Display
    st.header("Filter Results Summary")
    if not filtered_data.empty:
        st.write("### Details of Filtered Data:")
        optional_columns = ['soil_series', 'soil_texture', 'soil_type', 'nz_soil_classification']
        for column in optional_columns:
            if column in filtered_data.columns:
                st.write(f"**{column.replace('_', ' ').capitalize()}:** {filtered_data[column].unique()}")
    else:
        st.warning("No data available for the selected filters.")

    # Contamination Analysis with ICI
    st.header("Contamination Analysis")
    if 'ici' in filtered_data.columns:
        filtered_data['ici_class'] = filtered_data['ici'].apply(
            lambda x: "Low" if x < 1 else ("Moderate" if x <= 3 else "High")
        )
        # Define color map
        color_map = {"Low": "green", "Moderate": "yellow", "High": "red"}
        fig = px.scatter(
            filtered_data,
            x="site_num",
            y="ici",
            color="ici_class",
            color_discrete_map=color_map,
            title="ICI Levels with Classification",
            labels={"ici": "Integrated Contamination Index (ICI)"}
        )
        st.plotly_chart(fig)

        # Recommendations
        st.subheader("ICI Recommendations")
        st.write("- **Low (Green):** Maintain current soil management practices.")
        st.write("- **Moderate (Yellow):** Reduce contaminant inputs and consider enhancement strategies.")
        st.write("- **High (Red):** Immediate remediation required. Consult soil management experts.")
    else:
        st.warning("ICI data not available in the uploaded dataset.")

    # Download Filtered Data
    st.header("Download Filtered Data")
    filtered_csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_csv,
        file_name="filtered_soil_data.csv",
        mime="text/csv",
    )
else:
    st.info("Please upload a CSV or Excel file to view the dashboard.")
