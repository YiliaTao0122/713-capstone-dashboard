import streamlit as st
import pandas as pd
import plotly.express as px

# Title and Introduction
st.title("EcoSoil Insights: Auckland Soil Quality Monitoring Dashboard")
st.markdown("""
This interactive dashboard provides key insights into Auckland's soil quality, empowering landowners, policymakers, and agricultural practitioners 
to make data-driven decisions for sustainable land management.
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
    site_filter = st.sidebar.multiselect("Select Site Number", data['Site No.1'].unique())

    # Filter data
    filtered_data = data
    if land_use_filter:
        filtered_data = filtered_data[filtered_data['Land use'].isin(land_use_filter)]
    if period_filter:
        filtered_data = filtered_data[filtered_data['Period'].isin(period_filter)]
    if site_filter:
        filtered_data = filtered_data[filtered_data['Site No.1'].isin(site_filter)]

    # Header KPIs
    st.header("Key Performance Indicators")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Average pH", round(filtered_data['pH'].mean(), 2))
    kpi2.metric("Average Olsen P (mg/kg)", round(filtered_data['Olsen P'].mean(), 2))
    kpi3.metric("Average Bulk Density (g/cm³)", round(filtered_data['BD'].mean(), 2))

    # Tabs for Visualization
    st.header("Soil Quality Insights")
    tab1, tab2 = st.tabs(["Trace Element Hotspots", "Contamination Analysis"])

    # Tab 1: Trace Element Hotspots
    with tab1:
        st.subheader("Trace Element Hotspots")
        trace_elements = ['As', 'Cd', 'Cr', 'Cu', 'Ni', 'Pb', 'Zn']
        selected_trace = st.selectbox("Select a trace element to view hotspots", trace_elements)
        if selected_trace in filtered_data.columns:
            hotspot_chart = px.bar(
                filtered_data.groupby('Site No.1')[selected_trace].mean().reset_index(),
                x='Site No.1',
                y=selected_trace,
                title=f"Hotspots for {selected_trace}",
                labels={selected_trace: f"Average {selected_trace} (mg/kg)", 'Site No.1': "Site Number"},
                color=selected_trace,
            )
            st.plotly_chart(hotspot_chart)

    # Tab 2: Contamination Analysis
    with tab2:
        st.subheader("Contamination Levels")
        if 'ICI_Class' in filtered_data.columns:
            contamination_fig = px.pie(
                filtered_data,
                names='ICI_Class',
                title="Contamination Levels Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(contamination_fig)

        st.subheader("Contamination Level Trends")
        if 'ICI_Class' in filtered_data.columns:
            contamination_bar = px.bar(
                filtered_data.groupby('ICI_Class')['Site No.1'].count().reset_index(),
                x='ICI_Class',
                y='Site No.1',
                title="Number of Sites by Contamination Level",
                labels={'Site No.1': "Number of Sites", 'ICI_Class': "Contamination Level"},
                color='ICI_Class',
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(contamination_bar)

    # Recommendations
    st.header("Recommendations")
    recommendations = []
    if filtered_data['Olsen P'].mean() > 30:
        recommendations.append("⚠️ **High Olsen P Levels**: Reduce phosphate fertilizer usage and adopt slow-release alternatives.")
    if filtered_data['BD'].mean() > 1.5:
        recommendations.append("⚠️ **High Bulk Density**: Reduce soil compaction by minimizing heavy stocking during wet periods.")
    if 'ICI_Class' in filtered_data.columns and not filtered_data[filtered_data['ICI_Class'] == 'High'].empty:
        recommendations.append("⚠️ **High Contamination Sites Detected**: Monitor and remediate trace element contamination.")
    trace_thresholds = {'Cd': 0.6, 'Zn': 150}
    for element, threshold in trace_thresholds.items():
        if element in filtered_data.columns and filtered_data[element].mean() > threshold:
            recommendations.append(f"⚠️ **High {element} Levels**: Consider remediation to prevent toxicity risks.")
    if recommendations:
        st.subheader("Dynamic Recommendations")
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.markdown("✅ Soil quality metrics are within acceptable ranges.")

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
