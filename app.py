import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import requests
import geopandas as gpd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Load the data
data = pd.read_csv(
    'https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/World%20Energy%20Consumption.csv')

continents = pd.read_csv(
    'https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/country_continent_map.csv')

continent_geolocations = requests.get('https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/continents_geoLocation.json')
continent_geolocations=gpd.GeoDataFrame.from_features(continent_geolocations.json())


# Preprocess the data
continents = continents[['country', 'iso-3', 'region', 'subregion']]
regions = data.iso_code.replace(continents.set_index('iso-3')['region'])
data['region']=regions
data = data[data['iso_code'].notna()]
sub_regions = data.iso_code.replace(continents.set_index('iso-3')['subregion'])
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
#merge geolocation for each continent
oil_consumption_region = pd.merge(oil_consumption_region, continent_geolocations, left_on='region', right_on='CONTINENT')
oil_consumption_region.drop(columns=['CONTINENT'], inplace=True)

########################################################################

#generic function for every type of energy consumption plot worldwide
def fig_world_consu(variable, energy_type, yaxis_title):
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
    # Define the figure object
    fig_oil_consu_slider = go.Figure()

    # Loop through each unique year in the dataset and create a trace for each year
    for year in oil_consumption_region['year'].unique():
        # Filter the dataframe to only include data for the current year
        data_for_year = oil_consumption_region[oil_consumption_region['year'] == year]

        # Create a trace for the current year and add it to the figure
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

    # Add the layout to the figure
    fig_oil_consu_slider.update_layout(layout)

    return fig_oil_consu_slider

######################### BY CONTINENT ##################################
# def choropleth_by_continent():
    # Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(oil_consumption_region[oil_consumption_region['year'].isin([1970, 1980, 1990, 2000, 2010, 2019])], geometry='geometry')



fig12 = px.choropleth_mapbox(
    gdf,
    geojson=gdf.geometry,
    locations=gdf.index,
    color="oil_consumption",
    animation_frame='year',
    height=600,
    mapbox_style="carto-positron",
    color_continuous_scale="solar",
    opacity=0.5,
    zoom=1
).update_layout(margin={"l": 0, "r": 0, "b": 0, "t": 0},
                coloraxis_colorbar=dict(title="Oil Consumption (terawatt hour)"))

    # return fig

##########################################################################
oil_consumption_countries=oil_consumption_df[oil_consumption_df['country']!='World']

# Returns top 10 countries horizontal bar chart with slider over years
def top10_oil_consumption(variable, energy_type, xaxis_title):
    #create df for variable=variable
    top_10_df = data[data[variable].notna()][[variable, 'year', 'iso_code', 'country']]
    top_10_df = top_10_df[top_10_df['country']!='World']

    # Define the figure object
    top10_fig = go.Figure()

    # Loop through each unique year in the dataset and create a trace for each year
    for year in top_10_df['year'].unique():
        # Filter the dataframe to only include data for the current year
        data_for_year = top_10_df[top_10_df['year'] == year]

        # Sort the data by oil consumption in descending order and select the top 10 countries
        top_10_countries = data_for_year.sort_values(by=variable, ascending=True).tail(10)

        # Create a horizontal bar trace for the top 10 countries for the current year and add it to the figure
        top10_fig.add_trace(dict(type='bar',
                                            x=top_10_countries[variable],
                                            y=top_10_countries['country'].sort_values(ascending=True),
                                            orientation='h',
                                            showlegend=False,
                                            visible=False,
                                            marker=dict(color='orange'),
                                            hovertemplate='<b>%{y}</b> <br><b>' + energy_type + ' Consumption:</b> %{x:.1f}',
                                            name=''
                                            )
                                       )

    # First seen trace
    top10_fig.data[0].visible = True

    # Create a slider step for each year
    steps = []
    for i, year in enumerate(top_10_df['year'].unique()):
        visible_traces = [False] * len(top_10_df['year'].unique())
        visible_traces[i] = True
        step = dict(
            label=str(year),
            method="update",
            args=[{"visible": visible_traces},
                  {"title": "Top 10 countries with highest " + energy_type +  " consumption in " + str(year)},
                  {"yaxis": {"range": [0, 10]}}], # Set the y-axis range to display only the top 10 countries
        )
        steps.append(step)

    # Add slider to the layout
    sliders = [dict(
        active=0,
        steps=steps,
        currentvalue={"prefix": "Year: ", "font": {"size": 16}},
        len=1.0
    )]

    # Set the layout
    layout = dict(title=dict(text='Top 10 countries with highest oil consumption between 1965 and 2019'),
                  xaxis=dict(title=xaxis_title),
                  sliders=sliders,
                  plot_bgcolor='white'
                  )

    # Add the layout to the figure
    top10_fig.update_layout(layout)

    return top10_fig


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
    dcc.Tabs(id="energy_tabs", value='tab-1', children=[
        dcc.Tab(label='Oil', value='tab-1', children=[
            html.Br(),
            dcc.Tabs(id='oil-tabs', value='tab-1.1', children=[
                dcc.Tab(label='Worldwide', value='tab-1.1'),
                dcc.Tab(label='Continent', value='tab-1.2'),
                dcc.Tab(label='Country', value='tab-1.3')
            ])
        ]),
        dcc.Tab(label='Nuclear', value='tab-2', children=[html.Br(),
            dcc.Tabs(id='nuclear-tabs', value='tab-2.1', children=[
                dcc.Tab(label='Worldwide', value='tab-2.1'),
                dcc.Tab(label='Continent', value='tab-2.2'),
                dcc.Tab(label='Country', value='tab-2.3')
            ])
        ]),
        dcc.Tab(label='Coal', value='tab-3', children=[
    html.Br(),
            dcc.Tabs(id='coal-tabs', value='tab-3.1', children=[
                dcc.Tab(label='Worldwide', value='tab-3.1'),
                dcc.Tab(label='Continent', value='tab-3.2'),
                dcc.Tab(label='Country', value='tab-3.3')
            ])
        ]),
        dcc.Tab(label='Gas', value='tab-4', children=[
    html.Br(),
            dcc.Tabs(id='gas-tabs', value='tab-4.1', children=[
                dcc.Tab(label='Worldwide', value='tab-4.1'),
                dcc.Tab(label='Continent', value='tab-4.2'),
                dcc.Tab(label='Country', value='tab-4.3')
            ])
        ]),
    ],
    ),
    html.Div(id='tabs-content-example-graph')
])


@app.callback(dash.dependencies.Output('tabs-content-example-graph', 'children'),
              [dash.dependencies.Input('energy_tabs', 'value'),
              dash.dependencies.Input('oil-tabs', 'value'),
              dash.dependencies.Input('nuclear-tabs', 'value')])
def render_content(tab, oil_subtab, nuclear_subtab):
    if tab == 'tab-1':
        if oil_subtab == 'tab-1.1': #Oil worldwide
            return html.Div([
                
                dcc.Graph(id='fig_oil_consu_plot', figure=fig_world_consu('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)')),
                html.Br(),
                
            ])
        elif oil_subtab == 'tab-1.2': #oil by continent
            return html.Div([
                
                dcc.Graph(id='fig_oil_consu_slider',
                        figure=fig_oil_consu_slider()),
                html.Br(),
                # dcc.Graph(id="choropleth_oil", figure=fig12),
            ])
        elif oil_subtab == 'tab-1.3': #oil per country
            return html.Div([
                dcc.Graph(id='fig_oil_top_10',
                          figure=top10_oil_consumption('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)')),
                html.Br(),
            ])
    elif tab == 'tab-2':
        if nuclear_subtab == 'tab-2.1': #nuclear and worldwide
            return html.Div([
                html.H1(children='Nuclear Consumption'),
                dcc.Graph(id='fig_oil_consu_plot', figure=fig_world_consu('nuclear_consumption', 'Nuclear', 'Nuclear Energy Consumption (terawatt-hours)')),

            ])


if __name__ == '__main__':
    app.run_server(debug=True)
