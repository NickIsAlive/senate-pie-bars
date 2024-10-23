import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
import time

# Set up Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('/Users/nicholaslaskaridis/Senate-pie-visualiser/Raffle-Ticket-Visualiser/googlestuff.json', scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet (replace with your sheet ID)
sheet = client.open_by_key('1FnR8v9edEkiQwEcPEEGD92SKQqDHDPF6GHsl92lcirM').sheet1

def load_data():
    # Get values from A2:B12
    data = sheet.get('A2:B12')

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['Teacher', 'Tickets Sold'])

    # Ensure 'Tickets Sold' column is numeric
    df['Tickets Sold'] = pd.to_numeric(df['Tickets Sold'], errors='coerce')

    # Remove any rows with NaN values
    df = df.dropna()

    # Sort the DataFrame by 'Tickets Sold' in descending order
    df = df.sort_values('Tickets Sold', ascending=False)
    
    return df

# Streamlit app
st.title('Who will get pied?!')

# Create a placeholder for the chart
chart_placeholder = st.empty()

while True:
    df = load_data()

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

    # Update the chart in the placeholder
    chart_placeholder.plotly_chart(fig, config={'displayModeBar': False})  # Disable the mode bar which includes zoom/pan controls

    # Wait for 60 seconds before refreshing
    time.sleep(60)
