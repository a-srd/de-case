import pandas as pd
import plotly.graph_objects as go
from src.data_processing.utils import get_competitor_trials, get_competitor_trials_one_cond

def prepare_data():
    """
    Prepare the data for plotting.
    """
    competitor_trials_df = get_competitor_trials()
    competitor_trials_one_cond = get_competitor_trials_one_cond()
    sorted_sponsors = sorted(competitor_trials_df['Sponsor'].unique())
    bar_df = competitor_trials_df[["NCT Number", "Start Date", "Completion Date", "Sponsor", "Enrollment"]].copy()
    bar_df = pd.merge(bar_df, competitor_trials_one_cond[["NCT Number", "Group"]], on="NCT Number", how="inner")
    bar_df['Enrollment'] = bar_df['Enrollment'].astype(int)
    bar_df['Year'] = bar_df['Start Date'].str[:4].astype(int)
    bar_df['Completion Year'] = bar_df['Completion Date'].str[:4].astype(int)
    bar_df = bar_df.dropna(subset=['Year', 'Completion Year'])
    return bar_df, sorted_sponsors

def expand_data(bar_df):
    """
    Expand the data to include a row for each year that a study is active.
    """
    expanded_df = pd.DataFrame([(group, year, sponsor, enrollment)
                                for _, row in bar_df.iterrows()
                                for group in [row['Group']]
                                for year in range(row['Year'], row['Completion Year'] + 1)
                                for sponsor in [row['Sponsor']]
                                for enrollment in [row['Enrollment']]],
                               columns=['Group', 'Year', 'Sponsor', 'Enrollment'])
    grouped_df = expanded_df.groupby(['Group', 'Year', 'Sponsor'])['Enrollment'].sum().reset_index()
    return grouped_df

def create_plot(grouped_df, sorted_sponsors):
    """
    Create a stacked bar chart for each sponsor.
    """
    fig = go.Figure()
    buttons = []
    for sponsor in sorted(grouped_df['Sponsor'].unique()):
        df = grouped_df[grouped_df['Sponsor'] == sponsor]
        for group in df['Group'].unique():
            fig.add_trace(go.Bar(x=df[df['Group'] == group]['Year'], 
                                 y=df[df['Group'] == group]['Enrollment'], 
                                 name=group,
                                 visible=(sponsor == sorted_sponsors[0])))
        buttons.append(dict(method='update',
                            label=sponsor,
                            args=[{'visible': [sponsor == s for s in sorted_sponsors]}]))
    min_start_date = grouped_df['Year'].min()
    max_completion_date = grouped_df['Year'].max()
    years = list(range(min_start_date, max_completion_date + 1))
    fig.update_layout(
        title="Enrollment of Competitor Trials by Year",
        xaxis_title="Year",
        yaxis_title="Enrollment",
        xaxis=dict(
            range=[min_start_date, max_completion_date],
            tickvals=years,
            ticktext=years
        ),
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.2,
                yanchor="top"
            ),
        ],
        barmode='stack'
    )
    return fig

def main():
    """
    Main function to prepare data, expand data and create plot.
    """
    bar_df, sorted_sponsors = prepare_data()
    grouped_df = expand_data(bar_df)
    fig = create_plot(grouped_df, sorted_sponsors)
    return fig

if __name__ == "__main__":
    main()