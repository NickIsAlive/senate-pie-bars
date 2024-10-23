import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import requests
from io import StringIO

def load_data():
    # URL of the Google Sheet (replace with your sheet ID)
    sheet_id = '1FnR8v9edEkiQwEcPEEGD92SKQqDHDPF6GHsl92lcirM'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&range=A2:B12'

    # Fetch data from the Google Sheet
    response = requests.get(url)
    
    if response.status_code == 200:
        # Convert to DataFrame
        df = pd.read_csv(StringIO(response.text), header=None, names=['Teacher', 'Tickets Sold'])

        # Ensure 'Tickets Sold' column is numeric
        df['Tickets Sold'] = pd.to_numeric(df['Tickets Sold'], errors='coerce')

        # Remove any rows with NaN values
        df = df.dropna()

        # Sort the DataFrame by 'Tickets Sold' in descending order
        df = df.sort_values('Tickets Sold', ascending=False)
        
        return df
    else:
        st.error("Failed to fetch data from Google Sheet")
        return pd.DataFrame()

# Streamlit app
st.title('Who will get pied?!')

# Create a placeholder for the chart
chart_placeholder = st.empty()

# Initialize a counter for unique keys
chart_key = 0

while True:
    df = load_data()

    if not df.empty:
        # Create the custom bar chart
        fig = go.Figure()

        # Calculate color intensity based on tickets sold
        min_tickets = df['Tickets Sold'].min()
        max_tickets = df['Tickets Sold'].max()
        color_intensities = (df['Tickets Sold'] - min_tickets) / (max_tickets - min_tickets)

        # Add bars with color intensity (white to red)
        fig.add_trace(go.Bar(
            x=df['Teacher'],
            y=df['Tickets Sold'],
            text=df['Tickets Sold'],
            textposition='outside',
            marker_color=[f'rgba(255, {int(255 * (1 - intensity))}, {int(255 * (1 - intensity))}, 1)' for intensity in color_intensities],
            hoverinfo='none',
        ))

        # Customize the layout
        fig.update_layout(
            title='Tickets Sold per Teacher',
            xaxis_title='',
            yaxis_title='',
            xaxis_tickangle=-45,
            showlegend=False,
            height=600,
            width=800,
            yaxis=dict(showticklabels=False, showgrid=False, fixedrange=True),  # Combined yaxis settings
            plot_bgcolor='rgba(0,0,255,0)',
            dragmode=False,  # Disable drag mode
            xaxis=dict(fixedrange=True),  # Disable x-axis zoom
            bargap=0.3  # Increase the gap between bars
        )

        # Update the chart in the placeholder with a unique key
        chart_placeholder.plotly_chart(fig, config={'displayModeBar': False}, key=f"chart_{chart_key}")
        chart_key += 1  # Increment the key for the next iteration

    # Wait for 60 seconds before refreshing
    time.sleep(60)
