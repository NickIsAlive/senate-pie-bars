import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import requests
from io import StringIO
import numpy as np

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
st.title('Which teacher do you want to pie?!')

# Create a placeholder for the chart
chart_placeholder = st.empty()

# Initialize previous data and animation speed settings
previous_df = None
num_steps = 20  # Number of interpolation steps for smooth animation

# Initialize a counter for unique keys
chart_key = 0

while True:
    df = load_data()

    if not df.empty:
        # If this is the first load, set previous_df to avoid NoneType error
        if previous_df is None:
            previous_df = df.copy()

        # Get the current and target orders
        current_order = previous_df['Teacher'].tolist()
        target_order = df['Teacher'].tolist()

        # Calculate incremental steps for animation
        steps = []
        for i in range(num_steps + 1):
            # Interpolate values smoothly between previous and current data
            step_df = pd.DataFrame()
            
            # Interpolate positions for smooth reordering
            for teacher in current_order:
                current_idx = current_order.index(teacher)
                target_idx = target_order.index(teacher)
                
                # Calculate interpolated position
                pos = current_idx + (target_idx - current_idx) * (i / num_steps)
                
                # Get interpolated ticket value
                current_tickets = previous_df.loc[previous_df['Teacher'] == teacher, 'Tickets Sold'].iloc[0]
                target_tickets = df.loc[df['Teacher'] == teacher, 'Tickets Sold'].iloc[0]
                tickets = current_tickets + (target_tickets - current_tickets) * (i / num_steps)
                
                step_df = pd.concat([step_df, pd.DataFrame({
                    'Teacher': [teacher],
                    'Tickets Sold': [tickets],
                    'Position': [pos]
                })])
            
            # Sort by interpolated position
            step_df = step_df.sort_values('Position')
            steps.append(step_df)

        # Update chart at each interpolation step for smooth animation
        for step_df in steps:
            # Calculate color intensity based on tickets sold for the current step
            min_tickets = step_df['Tickets Sold'].min()
            max_tickets = step_df['Tickets Sold'].max()
            color_intensities = (step_df['Tickets Sold'] - min_tickets) / (max_tickets - min_tickets)

            # Update the figure with current interpolated data
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=step_df['Teacher'],
                y=step_df['Tickets Sold'],
                text=step_df['Tickets Sold'].astype(int),  # Ensure text displays as integers
                textposition='outside',
                marker=dict(
                    color=[f'rgba(255, {int(255 * (1 - intensity))}, {int(255 * (1 - intensity))}, 1)' 
                           for intensity in color_intensities],
                    line=dict(width=0)
                ),
                hoverinfo='none',
            ))

            # Update layout with smooth settings
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
                bargap=0.3
            )

            # Display the updated chart with a unique key
            chart_placeholder.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True, key=f"chart_{chart_key}")
            chart_key += 1  # Increment the key for the next chart

            # Short delay for each frame to animate smoothly
            time.sleep(0.05)

        # Store the current df as previous for the next update
        previous_df = df.copy()

    # Wait for 10 seconds before fetching new data
    time.sleep(10)