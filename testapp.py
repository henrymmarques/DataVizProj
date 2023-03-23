import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd

# Load the data
data = pd.read_csv('World Energy Consumption.csv')
continents = pd.read_csv('continents2.csv')
continents = continents[['name', 'alpha-3', 'region', 'sub-region']]
regions = data.iso_code.replace(continents.set_index('alpha-3')['region'])
data['region']=regions
data = data[data['iso_code'].notna()]
sub_regions = data.iso_code.replace(continents.set_index('alpha-3')['sub-region'])
data['sub_region']=sub_regions

oil_consumption_df=data[data['oil_consumption'].notna()][['oil_consumption', 'year', 'iso_code', 'country', 'region', 'sub_region' ]]

# Filter the data
world_data = oil_consumption_df[oil_consumption_df['country'] == 'World']

# Create the bar chart trace
trace_world = go.Bar(
    x=world_data['year'],
    y=world_data['oil_consumption'],
    text=world_data['oil_consumption'],
    texttemplate='%{y:.2s}',
    textposition='outside',
    cliponaxis=False,
    marker=dict(color='orange'),
    hovertemplate='<b>Year:</b> %{x}<br><b>Oil Consumption:</b> %{y:.1f}',
    name=''
)

# Create a dataframe with oil consumption by region and year
oil_consumption_region = oil_consumption_df.loc[oil_consumption_df['region']!='OWID_WRL'].groupby(['region', 'year']).sum()
oil_consumption_region = oil_consumption_region.reset_index()[['region', 'year', 'oil_consumption']]

# Create an empty graph object
fig_bar = go.Figure()
fig_bar2 = go.Figure()

# Loop through each unique year in the dataset and create a trace for each year
for year in oil_consumption_region['year'].unique():
    # Filter the dataframe to only include data for the current year
    data_for_year = oil_consumption_region[oil_consumption_region['year'] == year]
    # Create a trace for the current year
    fig_bar.add_trace(dict(type='bar',
                     x=data_for_year['region'],
                     y=data_for_year['oil_consumption'],
                     showlegend=False,
                     visible=False,
                     marker=dict(color='orange'),
                     hovertemplate='<b>%{x}</b> <br><b>Oil Consumption:</b> %{y:.1f}',
                     name=''
                    )
               )

# First seen trace
fig_bar.data[0].visible = True

# Create a slider step for each year
steps = []
for i, year in enumerate(oil_consumption_region['year'].unique()):
    visible_traces = [False] * len(oil_consumption_region['year'].unique())
    visible_traces[i] = True
    step = dict(
        label=str(year),
        method="update",
        args=[{"visible": visible_traces},
              {"title": "Oil consumption by continent in " + str(year)}],
    )
    steps.append(step)

# Add slider to the layout
sliders = [dict(
    active=0,
    steps=steps
)]

# Set the layout
layout = dict(title=dict(text='Oil consumption by continent between 1965 and 2019'),
              yaxis=dict(title='Oil Consumption (terawatt-hours)',
                         range=[0,2*(10**4)]
                        ),
              sliders=sliders,
              plot_bgcolor='white'
            )

# Add the traces to the figure
fig_bar.update_layout(layout)
fig_bar2.add_trace(trace_world)

# Create the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1(children='Oil Consumption'),
    dcc.Graph(id='oil_consumption', figure=fig_bar),
    html.Br(),
    dcc.Graph(id='oil_consumption 2 ', figure=fig_bar2),
])

if __name__ == '__main__':
    app.run_server(debug=True)