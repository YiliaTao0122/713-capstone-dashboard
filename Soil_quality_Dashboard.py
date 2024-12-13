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

    # Homepage: Filtered Data Table
    st.header("Filtered Soil Quality Data")
    columns_to_display = ['pH', 'TC %', 'TN %', 'Olsen P', 'AMN', 'BD', 'MP-5', 'MP-10']
    if not filtered_data.empty:
        def apply_thresholds(row):
            thresholds = {
                'pH': (5.5, 7.5),
                'TC %': (2.0, 4.0),
                'TN %': (0.2, 0.5),
                'Olsen P': (20, 40),
                'AMN': (50, 100),
                'BD': (1.0, 1.6),
                'MP-5': (10, 30),
                'MP-10': (5, 15)
            }
            styled_row = row.copy()
            for col, (low, high) in thresholds.items():
                if col in row:
                    if row[col] < low:
                        styled_row[col] = f"🔴 {row[col]}"
                    elif row[col] > high:
                        styled_row[col] = f"🟠 {row[col]}"
                    else:
                        styled_row[col] = f"🟢 {row[col]}"
            return styled_row

        styled_data = filtered_data[columns_to_display].apply(apply_thresholds, axis=1)
        st.dataframe(styled_data)
    else:
        st.warning("No data available for the selected filters.")

    # Header KPIs
    st.header("Key Performance Indicators")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Average pH", round(filtered_data['pH'].mean(), 2))
    kpi2.metric("Average Olsen P (mg/kg)", round(filtered_data['Olsen P'].mean(), 2))
    kpi3.metric("Average Bulk Density (g/cm³)", round(filtered_data['BD'].mean(), 2))

    # Tabs for Visualization
    st.header("Soil Quality Insights")
    tab1, tab2, tab3 = st.tabs(["Summary", "Contamination Analysis", "Geographical Insights"])

    # Tab 1: Summary
    with tab1:
        st.subheader("Soil Metrics by Land Use")
        metric_options = ['pH', 'TC %', 'TN %', 'Olsen P', 'AMN', 'BD']
        selected_metric = st.selectbox("Select a metric to view by Land Use", metric_options)
        if 'Land use' in filtered_data.columns:
            bar_chart = px.bar(
                filtered_data.groupby('Land use')[selected_metric].mean().reset_index(),
                x='Land use',
                y=selected_metric,
                title=f"Average {selected_metric} by Land Use",
                labels={selected_metric: f"Average {selected_metric}"},
            )
            st.plotly_chart(bar_chart)

        st.subheader("Time Series of Selected Metric")
        if 'Period' in filtered_data.columns:
            time_chart = px.line(
                filtered_data.groupby('Period')[selected_metric].mean().reset_index(),
                x='Period',
                y=selected_metric,
                title=f"{selected_metric} Trends Over Time",
                labels={selected_metric: f"{selected_metric}"}
            )
            st.plotly_chart(time_chart)

    # Tab 2: Contamination Analysis
    with tab2:
        st.subheader("Contamination Levels")
        if 'ICI' in filtered_data.columns:
            average_ici = filtered_data['ICI'].mean()
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=average_ici,
                title={'text': "Average ICI (Contamination Level)"},
                gauge={
                    'axis': {'range': [0, 3]},
                    'steps': [
                        {'range': [0, 1], 'color': "green"},
                        {'range': [1, 2], 'color': "yellow"},
                        {'range': [2, 3], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': average_ici
                    }
                }
            ))
            st.plotly_chart(fig)

            # Dynamic Recommendations
            st.subheader("Recommendations")
            if average_ici <= 1:
                st.markdown("- **Low Contamination**: Maintain current soil management practices.")
            elif 1 < average_ici <= 2:
                st.markdown("- **Moderate Contamination**: Reduce contaminant inputs and consider soil enhancement strategies.")
            else:
                st.markdown("- **High Contamination**: Immediate remediation required. Consult with soil management experts.")

    # Tab 3: Geographical Insights
    with tab3:
        st.subheader("Geographical Distribution of Monitoring Sites")
        if 'Latitude' in filtered_data.columns and 'Longitude' in filtered_data.columns:
            map_fig = px.scatter_mapbox(
                filtered_data,
                lat='Latitude',
                lon='Longitude',
                color='ICI_Class',
                size='Olsen P',
                hover_name='Site Num',
                title="Soil Monitoring Sites",
                mapbox_style="open-street-map"
            )
            st.plotly_chart(map_fig)

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
    st.info("Please upload a CSV or Excel file to view the dashboard.")
