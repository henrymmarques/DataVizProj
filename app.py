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
def fig_world_consu(variable, energy_type, yaxis_title, selected_year):
    # create df for variable=variable
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

    # Set the color of the bar for the selected year to be darker than the others
    trace_world.marker.color = ['orange' if year != selected_year else 'saddlebrown' for year in consumption_df['year']]

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

    return fig_consum
########################################################################

def fig_consu_slider(variable, energy_type, yaxis_title, year):

    consumption_slider_df = data[data[variable].notna()][[variable, 'year', 'iso_code', 'country', 'region', 'sub_region']]
    # Filter the dataframe to only include data for the specified year
    consumption_region_df = consumption_slider_df.loc[(consumption_slider_df['region'] != 'OWID_WRL') & (consumption_slider_df['year'] == year)].groupby([
                                                                                                        'region', 'year']).sum()
    consumption_region_df = consumption_region_df.reset_index()[['region', 'year', variable]]
    #merge geolocation for each continent
    consumption_region_df = pd.merge(consumption_region_df, continent_geolocations, left_on='region', right_on='CONTINENT')
    consumption_region_df.drop(columns=['CONTINENT'], inplace=True)

    # Define the figure object
    fig_consump_slider = go.Figure()

    # Create a trace for the current year and add it to the figure
    fig_consump_slider.add_trace(dict(type='bar',
                                        x=consumption_region_df['region'],
                                        y=consumption_region_df[variable],
                                        showlegend=False,
                                        visible=True,
                                        marker=dict(color='orange'),
                                        hovertemplate='<b>%{x}</b> <br><b>' + energy_type + ' Consumption:</b> %{y:.1f}',
                                        name=''
                                        )
                                   )

    # Set the layout
    layout = dict(title=dict(text=energy_type+ ' consumption by continent in '+ str(year)),
                  yaxis=dict(title=yaxis_title,
                             range=[0, 2*(10**4)]
                             ),
                  plot_bgcolor='white'
                  )

    # Add the layout to the figure
    fig_consump_slider.update_layout(layout)

    return fig_consump_slider
"""
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
"""


def update_top10_graph(variable, energy_type, xaxis_title, year):
    top10_fig = go.Figure()
    # Create df for variable=variable
    top_10_df = data[data[variable].notna()][[variable, 'year', 'iso_code', 'country']]
    top_10_df = top_10_df[top_10_df['country']!='World']

    # Filter the dataframe to only include data for the selected year
    data_for_year = top_10_df[top_10_df['year'] == year]

    # Sort the data by oil consumption in descending order and select the top 10 countries
    top_10_countries = data_for_year.sort_values(by=variable, ascending=True).tail(10)

    # Remove any existing traces from the figure
    top10_fig.data = []

    # Create a horizontal bar trace for the top 10 countries for the selected year and add it to the figure
    top10_fig.add_trace(dict(
        type='bar',
        x=top_10_countries[variable],
        y=top_10_countries.sort_values(by=variable, ascending=True)['country'],
        orientation='h',
        showlegend=False,
        marker=dict(color='orange'),
        hovertemplate='<b>%{y}</b> <br><b>' + energy_type + ' Consumption:</b> %{x:.1f}',
        name=''
    ))

    # Set the layout
    top10_fig.update_layout(
        title=dict(text='Top 10 countries with highest ' + energy_type +' consumption in ' + str(year)),
        xaxis=dict(title=xaxis_title),
        plot_bgcolor='white'
    )

    return top10_fig


# Creates choropleth by country with a slider by year. Some energy consumption
def create_choropleth_map(variable, energy_type, year):
    
    # df for oil_consumption plots
    consumption_df = data[data[variable].notna()][[variable, 'year', 'iso_code', 'country']]

    # Filter data for the given year
    oil_data_year = consumption_df[consumption_df["year"] == year]

    # Define the choropleth map
    fig = go.Figure(go.Choropleth(
        locations=oil_data_year["iso_code"],
        z=oil_data_year[variable],
        colorscale="YlOrRd",
        zmin=0,
        zmax=1000,
        marker_line_width=0.5,
        marker_line_color="white",
        text=oil_data_year["country"],
        hovertemplate="<b>%{text}</b><br>" + energy_type + " Consumption: %{z:.2f}",
        name=''
    ))

    # Load high resolution world map
    fig.update_geos(
        resolution=110,
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor="white",
        countrycolor="lightgray",
        coastlinecolor="lightgray",
        oceancolor="lightblue"
    )

    # Update the layout of the map
    fig.update_layout(
        title= energy_type + " Consumption per Country in {}".format(year),
        geo_scope="world",
        margin={"l": 0, "r": 0, "t": 50, "b": 0},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=16, color='black'), ##all font
        height=800
    )
    
    # Update the title with the current year
    fig.update_layout(title={"text": energy_type + " Consumption per Country in {}".format(year), "font": {"size": 24}})

    return fig

################### COMPONENTS #######################
# Define the slider marks for every 10 years
slider_marks = {str(year): {'label': str(year), 'style': {'writing-mode': 'vertical-lr', 'text-orientation': 'mixed'}} for year in range(1965, 2020, 10)}
initial_top10_fig = update_top10_graph('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)



######################################################

# Create the app
app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1('World Energy Data', style={'textAlign': 'center'}),
    dcc.Tabs(id="energy_tabs", value='tab-1', children=[
        dcc.Tab(label='Oil', value='tab-1', children=[
            
            html.Br(),
            dcc.Slider(id='year-slider', min=1965, max=2019, value=1965, marks=slider_marks, step=None),
            html.Br()
        ]),
        dcc.Tab(label='Coal', value='tab-2'),

        dcc.Tab(label='Renewables', value='tab-3'),
        dcc.Tab(label='Comparison', value='tab-4')
        ]
    ),
    html.Div(id='tabs-content-example-graph')
])


@app.callback(dash.dependencies.Output('tabs-content-example-graph', 'children'),
              [dash.dependencies.Input('energy_tabs', 'value'),
              dash.dependencies.Input('year-slider', 'value')])
def render_content(tab, year):
    if tab == 'tab-1':
           
            return html.Div([
                 dcc.Graph(id='fig_oil_consu_plot', figure=fig_world_consu('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', year)),
                 dcc.Graph(id='fig_oil_consu_slider', figure=fig_consu_slider('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', year)),
                html.Br(),
                dcc.Graph(id='fig_oil_top_10', figure=update_top10_graph('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', year)),

                html.Br(),
                dcc.Graph(id='fig_oil_choropleth',
                          figure=create_choropleth_map('oil_consumption', 'Oil', year)),
                html.Br(),
                
            ])
    elif tab == 'tab-2':
            return html.Div([
                
                dcc.Graph(id='fig_coal_consu_plot', figure=fig_world_consu('coal_consumption', 'Coal', 'Coal Consumption (terawatt-hours)')),
                html.Br(),
                 dcc.Graph(id='fig_coal_consu_slider',
                        figure=fig_consu_slider('coal_consumption', 'Coal', 'Coal Consumption (terawatt-hours)')),
                html.Br(),
                html.Br(),
                
                dcc.Graph(id='fig_coal_choropleth',
                          figure=create_choropleth_map('coal_consumption', 'Coal')),
                html.Br(),
            ])


if __name__ == '__main__':
    app.run_server(debug=True)
