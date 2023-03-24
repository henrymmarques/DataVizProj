import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Load the data
data = pd.read_csv(
    'https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/World%20Energy%20Consumption.csv')
continents = pd.read_csv(
    'https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/continents2.csv')

# Preprocess the data
continents = continents[['name', 'alpha-3', 'region', 'sub-region']]
regions = data.iso_code.replace(continents.set_index('alpha-3')['region'])
data['region'] = regions
data = data[data['iso_code'].notna()]
sub_regions = data.iso_code.replace(
    continents.set_index('alpha-3')['sub-region'])
data['sub_region'] = sub_regions

# df for oil_consumption plots
oil_consumption_df = data[data['oil_consumption'].notna()][['oil_consumption', 'year', 'iso_code', 'country', 'region', 'sub_region']]

# Filter the data
world_data = oil_consumption_df[oil_consumption_df['country'] == 'World']


# Create a dataframe with oil consumption by region and year
oil_consumption_region = oil_consumption_df.loc[oil_consumption_df['region'] != 'OWID_WRL'].groupby([
                                                                                                    'region', 'year']).sum()
oil_consumption_region = oil_consumption_region.reset_index()[
    ['region', 'year', 'oil_consumption']]

########################################################################

#generic function for every type of energy consumption plot worldwide
def fig_consu(variable, energy_type, yaxis_title):
    #create df for variable=variable
    consumption_df = data[data[variable].notna()][[variable, 'year', 'iso_code', 'country', 'region', 'sub_region']]
    # Filter the data
    consumption_df = consumption_df[consumption_df['country'] == 'World']

    # Create the bar chart trace
    trace_world = go.Bar(
        x=consumption_df['year'],
        y=consumption_df[variable],
        text=consumption_df[variable],
        texttemplate='%{y:.2s}',
        textposition='outside',
        cliponaxis=False,
        marker=dict(color='orange'),
        hovertemplate='<b>Year:</b> %{x}<br><b>' + energy_type + ' Consumption:</b> %{y:.1f}',
        name=''
    )

    # create the layout
    layout_world = go.Layout(
        title=f'WorldWide {energy_type} Consumption by Year',
        xaxis=dict(
            title='Year',
            tickmode='linear',
            dtick=1,
            tickangle=270
        ),
        yaxis=dict(
            title=yaxis_title
        ),
        plot_bgcolor='white',
        hoverlabel=dict()
    )
    fig_consum = go.Figure(data=trace_world, layout=layout_world)
    # fig_oil_consu.add_trace(trace_world)

    return fig_consum
########################################################################


def fig_oil_consu_slider():
    # Loop through each unique year in the dataset and create a trace for each year
    for year in oil_consumption_region['year'].unique():
        # Filter the dataframe to only include data for the current year
        data_for_year = oil_consumption_region[oil_consumption_region['year'] == year]
        fig_oil_consu_slider = go.Figure()
        # Create a trace for the current year
        fig_oil_consu_slider.add_trace(dict(type='bar',
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
    fig_oil_consu_slider.data[0].visible = True

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
                             range=[0, 2*(10**4)]
                             ),
                  sliders=sliders,
                  plot_bgcolor='white'
                  )

    # Add the traces to the figure
    fig_oil_consu_slider.update_layout(layout)
    return fig_oil_consu_slider
# 


# Create the app
app = dash.Dash(__name__)
server = app.server

# /////////// SEM TABS /////////
# # Define the layout
# app.layout = html.Div([
#     html.H1(children='Oil Consumption'),
#     dcc.Graph(id='fig_oil_consu_slider', figure=fig_oil_consu_slider()),
#     html.Br(),
#     dcc.Graph(id='fig_oil_consu_plot', figure=fig_oil_consu_plot()),
# ])
# ///////////////////////////////


app.layout = html.Div([
    html.H1('World Energy Data', style={'textAlign': 'center'}),
    dcc.Tabs(id="tabs-example-graph", value='tab-1', children=[
        dcc.Tab(label='Oil', value='tab-1'),
        dcc.Tab(label='Nuclear', value='tab-2'),
        dcc.Tab(label='Coal', value='tab-3'),
        dcc.Tab(label='Gas', value='tab-4'),
    ],
    ),
    html.Div(id='tabs-content-example-graph')
])


@app.callback(dash.dependencies.Output('tabs-content-example-graph', 'children'),
              dash.dependencies.Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            
            dcc.Graph(id='fig_oil_consu_slider',
                      figure=fig_oil_consu_slider()),
            html.Br(),
            dcc.Graph(id='fig_oil_consu_plot', figure=fig_consu('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)')),
            html.Br(),
            
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H1(children='Nuclear Consumption'),
            dcc.Graph(id='fig_oil_consu_plot', figure=fig_consu('nuclear_consumption', 'Nuclear', 'Nuclear Energy Consumption (terawatt-hours)')),

        ])


if __name__ == '__main__':
    app.run_server(debug=True)
