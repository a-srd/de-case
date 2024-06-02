import pandas as pd
from datetime import datetime, timedelta
from src.api_client.client import ClinicalTrials
import plotly.graph_objects as go
import pycountry
from src.data_processing.utils import get_geographic_data

def prepare_data():
    """
    Prepare the data for plotting.
    """
    geo_df = get_geographic_data()
    count_df = geo_df.groupby(['Country Code', 'Sponsor']).size().reset_index(name='Count')
    return count_df

def create_dropdown(count_df):
    """
    Create a dropdown menu.
    """
    dropdown = [{'label': sponsor, 'method': 'update', 'args': [{'visible': [sponsor == s for s in count_df['Sponsor'].unique()]}]} for sponsor in count_df['Sponsor'].unique()]
    return dropdown

def create_traces(count_df):
    """
    Add one trace for each sponsor.
    """
    traces = []
    for sponsor in count_df['Sponsor'].unique():
        traces.append(
            go.Choropleth(
                locations=count_df.loc[count_df['Sponsor'] == sponsor, 'Country Code'],
                z=count_df.loc[count_df['Sponsor'] == sponsor, 'Count'],
                name=sponsor,
                visible=(sponsor == count_df['Sponsor'].unique()[0]),  # Only the first trace is visible
                colorscale='Blues'  # Change color gradient to light blue to dark
            )
        )
    return traces

def create_plot(dropdown, traces):
    """
    Create a base Choropleth map that will be updated based on the dropdown selection.
    """
    fig = go.Figure(data=traces)
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=dropdown,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.09,
                xanchor="left",
                y=1.01,  # Adjust this value to move the dropdown up or down
                yanchor="bottom"  # Anchor the dropdown to the bottom of the y position
            ),
        ]
    )
    fig.show()

def main():
    """
    Main function to prepare data, create dropdown, create traces and create plot.
    """
    count_df = prepare_data()
    dropdown = create_dropdown(count_df)
    traces = create_traces(count_df)
    create_plot(dropdown, traces)

if __name__ == "__main__":
    main()