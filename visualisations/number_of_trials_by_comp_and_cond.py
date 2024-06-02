import plotly.graph_objects as go
from src.data_processing.utils import get_competitor_trials, get_competitor_trials_one_cond

def prepare_data():
    """
    Prepare the data for plotting.
    """
    competitor_trials_df = get_competitor_trials()
    competitor_trials_one_cond = get_competitor_trials_one_cond()
    pivot_table = competitor_trials_one_cond.pivot_table(index='Sponsor', columns='Group', aggfunc='size', fill_value=0)
    pivot_table = pivot_table.reindex(pivot_table.sum(axis=1).sort_values(ascending=True).index)
    return pivot_table

def create_traces(pivot_table):
    """
    Create a list of traces, one for each condition group.
    """
    traces = [go.Bar(name=group, y=pivot_table.index, x=pivot_table[group], orientation='h') 
              for group in pivot_table.columns]
    return traces

def create_plot(traces):
    """
    Create a Figure and add the traces.
    """
    layout = go.Layout(
        title="Number of Trials by Competitor and Condition",
        xaxis_title="Number of References to Condition in a Trial",
        yaxis_title="Sponsor",
        barmode='stack'
    )
    fig = go.Figure(data=traces, layout=layout)
    fig.show()

def main():
    """
    Main function to prepare data, create traces and create plot.
    """
    pivot_table = prepare_data()
    traces = create_traces(pivot_table)
    create_plot(traces)

if __name__ == "__main__":
    main()