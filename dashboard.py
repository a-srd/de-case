import dash
import dash_core_components as dcc
import dash_html_components as html

from visualisations.intervetion_type_pie_chart import main as intervention_type_pie_chart
from visualisations.enrollment_of_comp_trial_by_year import main as enrollment_of_comp_trial_by_year
from visualisations.geographic_distribution_of_comp_trials import main as geographic_distribution_of_comp_trials
from visualisations.number_of_studies_per_year import main as number_of_studies_per_year
from visualisations.number_of_trials_by_comp_and_cond import main as number_of_trials_by_comp_and_cond
from visualisations.total_enrollment_per_year import main as total_enrollment_per_year
from visualisations.trials_by_competitor_and_phase import main as trials_by_competitor_and_phase


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.layout = html.Div([
    html.H1("Competitor Analysis Dashboard",
            style={
                'textAlign': 'center',  # Center align the text
                'color': '#007BFF',  # Set the text color
                'padding': '10px',  # Add some padding
                'borderRadius': '5px',  # Add rounded corners
                'margin': '20px 0',  # Add some margin at the top and bottom
                'fontFamily': '"Open Sans", verdana, arial, sans-serif'
            }),
    html.P("This dashboard provides a visual analysis of competitor trials. It includes various graphs that represent different aspects of the trials, such as the type of intervention, enrollment by year, geographic distribution, number of studies per year, and total enrollment per year. The competitors are identified by the sponsors of trials marked as funded by industrial sources and having a significant overlap in disease area focus as Novo Nordisk A/S.",
           style={
               'textAlign': 'center',  # Center align the text
               'color': '#000000',  # Set the text color
               'padding': '10px',  # Add some padding
               'fontFamily': '"Open Sans", verdana, arial, sans-serif'
           }),
    html.Div([
        html.Div(dcc.Graph(id='graph1', figure=intervention_type_pie_chart()), className='six columns'),
        html.Div(dcc.Graph(id='graph2', figure=enrollment_of_comp_trial_by_year()), className='six columns'),
    ], className='row'),
    html.Div([
        html.Div(dcc.Graph(id='graph3', figure=geographic_distribution_of_comp_trials()), className='six columns'),
        html.Div(dcc.Graph(id='graph4', figure=number_of_studies_per_year()), className='six columns'),
    ], className='row'),
    html.Div([
        html.Div(dcc.Graph(id='graph5', figure=number_of_trials_by_comp_and_cond()), className='twelve columns'),
    ], className='row'),
    html.Div([
        html.Div(dcc.Graph(id='graph6', figure=total_enrollment_per_year()), className='twelve columns'),
    ], className='row'),
    html.Div(dcc.Graph(id='graph7', figure=trials_by_competitor_and_phase()), className='twelve columns'),
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)