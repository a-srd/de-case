import pandas as pd
import plotly.express as px
from src.data_processing.utils import get_competitor_trials, get_competitor_trials_one_cond

def prepare_data():
    """
    Prepare the data for plotting.
    """
    competitor_trials_df = get_competitor_trials()
    competitor_trials_one_cond = get_competitor_trials_one_cond()[["NCT Number", "Group"]]
    competitor_trials_df = pd.merge(competitor_trials_df, competitor_trials_one_cond, on="NCT Number", how="inner")
    competitor_trials_df = competitor_trials_df[["NCT Number",'Start Date', 'Completion Date', 'Group', 'Sponsor']]
    competitor_trials_df['Year'] = competitor_trials_df['Start Date'].str[:4].astype(int)
    competitor_trials_df['Completion Year'] = competitor_trials_df['Completion Date'].str[:4].astype(int)
    competitor_trials_df = competitor_trials_df.dropna(subset=['Year', 'Completion Year'])
    competitor_trials_df['Year'] = competitor_trials_df['Year'].astype(int)
    competitor_trials_df['Completion Year'] = competitor_trials_df['Completion Year'].astype(int)
    expanded_df = pd.DataFrame([(group, year)
                                for _, row in competitor_trials_df.iterrows()
                                for group in [row['Group']]
                                for year in range(row['Year'], row['Completion Year'] + 1)],
                               columns=['Group', 'Year'])
    grouped_df = expanded_df.groupby(['Group', 'Year']).size().reset_index(name='Count')
    return grouped_df

def create_plot(grouped_df):
    """
    Create a stacked line graph.
    """
    fig = px.line(grouped_df, x='Year', y='Count', color='Group', line_group='Group', 
                  labels={'Count':'Number of Studies'}, title='Number of Studies per Year')
    return fig

def main():
    """
    Main function to prepare data and create plot.
    """
    grouped_df = prepare_data()
    fig = create_plot(grouped_df)
    return fig

if __name__ == "__main__":
    main()