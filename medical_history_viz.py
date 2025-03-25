import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_parameter_trend_chart(history_data, parameter):
    """Create an interactive line chart for a specific parameter over time"""
    fig = px.line(
        history_data,
        x='date',
        y=parameter,
        title=f'{parameter} Trend Over Time',
        markers=True
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=parameter,
        hovermode='x unified'
    )
    return fig

def create_multi_parameter_chart(history_data, parameters):
    """Create a multi-line chart for comparing multiple parameters"""
    fig = go.Figure()

    for param in parameters:
        fig.add_trace(
            go.Scatter(
                x=history_data['date'],
                y=history_data[param],
                name=param,
                mode='lines+markers'
            )
        )

    fig.update_layout(
        title="Multiple Parameters Comparison",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode='x unified',
        showlegend=True
    )
    return fig

def create_radar_chart(latest_data, reference_ranges):
    """Create a radar chart showing current values against reference ranges"""
    fig = go.Figure()

    # Add reference range area
    fig.add_trace(go.Scatterpolar(
        r=reference_ranges['upper'],
        theta=reference_ranges['parameter'],
        fill='toself',
        name='Normal Range',
        fillcolor='rgba(0,255,0,0.2)',
        line_color='rgba(0,255,0,0.5)'
    ))

    # Add current values
    fig.add_trace(go.Scatterpolar(
        r=latest_data['value'],
        theta=latest_data['parameter'],
        name='Current Values',
        line_color='rgb(255,0,0)',
        marker_symbol='star'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(reference_ranges['upper']) * 1.2]
            )),
        showlegend=True,
        title="Current Values vs. Reference Ranges"
    )
    return fig

def generate_sample_data():
    """Generate sample medical history data for demonstration"""
    try:
        # Use 'ME' (month end) instead of deprecated 'M'
        dates = pd.date_range(end=datetime.now(), periods=10, freq='ME')

        data = pd.DataFrame({
            'date': dates,
            'RBC': np.random.normal(4.5, 0.5, 10),
            'HGB': np.random.normal(14, 1, 10),
            'MCV': np.random.normal(88, 4, 10),
            'MCH': np.random.normal(30, 2, 10),
            'MCHC': np.random.normal(33, 2, 10),
            'RDW': np.random.normal(13, 1, 10)
        })

        return data
    except Exception as e:
        st.error(f"Error generating sample data: {str(e)}")
        return None

def get_reference_ranges():
    """Get reference ranges for blood parameters"""
    return {
        'parameter': ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW'],
        'lower': [4.0, 12.0, 80.0, 27.0, 32.0, 11.5],
        'upper': [5.5, 16.0, 100.0, 32.0, 36.0, 14.5]
    }

def show_medical_history_visualization():
    """Main function to display medical history visualization"""
    try:
        st.header("Medical History Visualization")

        # Generate sample data (replace with actual data when available)
        history_data = generate_sample_data()

        if history_data is not None:
            # Parameter selection
            st.subheader("Parameter Trends")
            selected_parameter = st.selectbox(
                "Select parameter to visualize",
                ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW']
            )

            # Show individual parameter trend
            trend_chart = create_parameter_trend_chart(history_data, selected_parameter)
            st.plotly_chart(trend_chart, use_container_width=True)

            # Multi-parameter comparison
            st.subheader("Multi-parameter Comparison")
            selected_params = st.multiselect(
                "Select parameters to compare",
                ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW'],
                default=['RBC', 'HGB']
            )

            if selected_params:
                multi_param_chart = create_multi_parameter_chart(history_data, selected_params)
                st.plotly_chart(multi_param_chart, use_container_width=True)

            # Radar chart with reference ranges
            st.subheader("Current Values vs Reference Ranges")
            latest_data = pd.DataFrame({
                'parameter': ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW'],
                'value': history_data.iloc[-1][['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW']].values
            })

            reference_ranges = get_reference_ranges()
            radar_chart = create_radar_chart(latest_data, reference_ranges)
            st.plotly_chart(radar_chart, use_container_width=True)
        else:
            st.warning("Unable to load medical history data. Please try again later.")
    except Exception as e:
        st.error(f"Error displaying medical history visualization: {str(e)}")