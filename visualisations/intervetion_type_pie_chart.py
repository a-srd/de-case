from src.data_processing.utils import get_competitor_trials
import plotly.graph_objects as go

def prepare_data():
    """
    Prepare the data for plotting.
    """
    intervention_df = get_competitor_trials()
    intervention_df["Intervention Type"] = intervention_df["Interventions"].str.split(":").str[0]
    value_counts = intervention_df[intervention_df["Intervention Type"] != '']["Intervention Type"].value_counts(dropna=True)
    labels = value_counts.index
    return labels, value_counts

def create_plot(labels, value_counts):
    """
    Create a pie chart.
    """
    fig = go.Figure(data=[go.Pie(labels=labels, values=value_counts, hole=.3)])
    fig.update_layout(title_text="Intervention Type of Competitor Trials")
    return fig  # Return the figure instead of showing it

def main():
    """
    Main function to prepare data and create plot.
    """
    labels, value_counts = prepare_data()
    fig = create_plot(labels, value_counts)
    return fig  # Return the figure created by create_plot

if __name__ == "__main__":
    main()