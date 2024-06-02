import plotly.graph_objects as go
from src.data_processing.utils import get_competitor_trials

def prepare_data():
    """
    Prepare the data for plotting.
    """
    competitor_trials_df = get_competitor_trials()
    competitor_trials_df['Phases'] = competitor_trials_df['Phases'].replace('', 'Not Reported')
    order = ['PHASE1', 'PHASE1|PHASE2', 'PHASE2', 'PHASE2|PHASE3', 'PHASE3', 'PHASE4', 'NA', 'Not Reported']
    order = ['PHASE1', 'PHASE1|PHASE2', 'PHASE2', 'PHASE2|PHASE3', 'PHASE3', 'PHASE4', 'NA', 'Not Reported']
    pivot_table = competitor_trials_df.pivot_table(index='Sponsor', columns='Phases', aggfunc='size', fill_value=0)

    # Subset the DataFrame with only the elements of 'order' that are present in the DataFrame's columns
    order = [phase for phase in order if phase in pivot_table.columns]
    pivot_table = pivot_table[order]
    return pivot_table

def create_traces(pivot_table):
    """
    Create a list of traces, one for each phase.
    """
    colors = ['#add8e6', '#87cefa', '#87ceeb', '#1e90ff', '#4169e1', '#0000ff', '#0000cd', '#00008b']
    traces = [go.Bar(name=phase, y=pivot_table.index, x=pivot_table[phase], orientation='h', marker_color=color) 
              for phase, color in zip(pivot_table.columns, colors)]
    return traces

def create_plot(traces):
    """
    Create a Figure and add the traces.
    """
    layout = go.Layout(
        title="Number of Trials by Competitor and Phase",
        xaxis_title="Number of Trials",
        yaxis_title="Competitor",
        barmode='stack'
    )
    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(legend_traceorder="normal")
    return fig

def main():
    """
    Main function to prepare data, create traces and create plot.
    """
    pivot_table = prepare_data()
    traces = create_traces(pivot_table)
    fig = create_plot(traces)
    return fig

if __name__ == "__main__":
    main()