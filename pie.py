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

# Initialize previous data as None
prev_df = None

while True:
    df = load_data()

    if not df.empty:
        # Create the custom bar chart
        fig = go.Figure()

        # Calculate color intensity based on tickets sold
        min_tickets = df['Tickets Sold'].min()
        max_tickets = df['Tickets Sold'].max()
        color_intensities = (df['Tickets Sold'] - min_tickets) / (max_tickets - min_tickets)

        # If we have previous data, create frames for animation
        frames = []
        if prev_df is not None:
            # Create 30 intermediate frames for smooth animation
            for i in range(30):
                frame_df = pd.DataFrame()
                frame_df['Teacher'] = df['Teacher']
                frame_df['Tickets Sold'] = prev_df['Tickets Sold'] + (df['Tickets Sold'] - prev_df['Tickets Sold']) * (i/29)
                
                # Sort the frame data to match current order
                frame_df = frame_df.set_index('Teacher').reindex(df['Teacher']).reset_index()
                
                # Calculate color intensities for frame
                frame_min = frame_df['Tickets Sold'].min()
                frame_max = frame_df['Tickets Sold'].max()
                frame_intensities = (frame_df['Tickets Sold'] - frame_min) / (frame_max - frame_min)
                
                frames.append(go.Frame(
                    data=[go.Bar(
                        x=frame_df['Teacher'],
                        y=frame_df['Tickets Sold'],
                        text=frame_df['Tickets Sold'].round().astype(int),
                        textposition='outside',
                        marker=dict(
                            color=[f'rgba(255, {int(255 * (1 - intensity))}, {int(255 * (1 - intensity))}, 1)' 
                                  for intensity in frame_intensities],
                            line=dict(width=0)
                        ),
                        hoverinfo='none'
                    )]
                ))

        # Add the main bar trace
        fig.add_trace(go.Bar(
            x=df['Teacher'],
            y=df['Tickets Sold'],
            text=df['Tickets Sold'],
            textposition='outside',
            marker=dict(
                color=[f'rgba(255, {int(255 * (1 - intensity))}, {int(255 * (1 - intensity))}, 1)' 
                      for intensity in color_intensities],
                line=dict(width=0)
            ),
            hoverinfo='none',
        ))

        # Add frames to the figure
        fig.frames = frames

        # Customize the layout
        fig.update_layout(
            title='Tickets Sold per Teacher',
            xaxis_title='',
            yaxis_title='',
            xaxis_tickangle=-45,
            showlegend=False,
            height=600,
            width=800,
            yaxis=dict(showticklabels=False, showgrid=False, fixedrange=True),
            plot_bgcolor='rgba(0,0,255,0)',
            dragmode=False,
            xaxis=dict(fixedrange=True),
            bargap=0.3,
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 20, 'redraw': True},
                        'fromcurrent': True,
                        'mode': 'immediate'
                    }]
                }],
                'visible': False
            }]
        )

        # Update the chart and store current data as previous
        chart_placeholder.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)
        prev_df = df.copy()

    # Wait for 10 seconds before refreshing
    time.sleep(10)
