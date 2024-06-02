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

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Visualizations"),
    dcc.Graph(id='graph1', figure=intervention_type_pie_chart()),
    dcc.Graph(id='graph2', figure=enrollment_of_comp_trial_by_year()),
    dcc.Graph(id='graph3', figure=geographic_distribution_of_comp_trials()),
    dcc.Graph(id='graph4', figure=number_of_studies_per_year()),
    dcc.Graph(id='graph5', figure=number_of_trials_by_comp_and_cond()),
    dcc.Graph(id='graph6', figure=total_enrollment_per_year()),
    dcc.Graph(id='graph7', figure=trials_by_competitor_and_phase()),
])

if __name__ == '__main__':
    app.run_server(debug=True)