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
            dtick=5,
            tickangle=270
        ),
        yaxis=dict(
            title=yaxis_title
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'), ##all font
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
                     plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white') ##all font
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


def fig_top10_graph(variable, energy_type, xaxis_title, year):
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
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white') ##all font
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
        name='',
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
        oceancolor="lightblue",
        showocean=True
    )

    # Update the layout of the map
    fig.update_layout(
        title= energy_type + " Consumption per Country in {}".format(year),
        geo_scope="world",
        margin={"l": 0, "r": 30, "t": 50, "b": 0},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color='white'), ##all font
        # height=800
    )
    
    # Update the title with the current year
    fig.update_layout(title={"text": energy_type + " Consumption per Country in {}".format(year), "font": {"size": 24}})

    return fig

#Creates stacked bar chart for renewables
def stacked_renewables(year, energies=None):
    energy_columns = ['other_renewable_consumption', 'solar_consumption', 'wind_consumption', 'hydro_consumption', 'biofuel_consumption']
    if energies==None:
        energies=energy_columns
    renewables = data[['country', 'region', 'year'] + energy_columns]
    renewables_year = renewables[renewables['year'] == year][['region'] + energy_columns]
    renewables_year = renewables_year[renewables_year['region'].isin(['Africa', 'Asia', 'Europe', 'North America', 'Oceania', 'South America'])]
    # Calculate the total consumption for each region
    renewables_year_totals = renewables_year.groupby('region').sum()
    # Calculate the percentage of each energy source for each region
    df_perc = renewables_year_totals.apply(lambda x: x / x.sum() * 100, axis=1)
    # format input to match variable names
    # energies= [(x+'_consumption').lower() if ' ' not in x else (x.replace(' ', '_') + '_consumption').lower() for x in energies]
    # Filter by energies list
    df_perc = df_perc[energies]
        
    #  Set colors for the different types of energy
    colors = {'other_renewable_consumption': '#0066CC',
            'solar_consumption': '#FFD700',
            'wind_consumption': '#92C6FF',
            'hydro_consumption': '#003366',
            'biofuel_consumption': '#008000'}

    # Create the stacked bar chart
    fig = go.Figure(data=[go.Bar(
        x=df_perc.index,
        y=df_perc[col],
        name=col.split('_')[0].capitalize(),
        marker_color=colors[col],
        hovertemplate="<b>%{y:.2f}%</b> " + col.split('_')[0].capitalize() +" Consumption <extra></extra>"
    ) for col in df_perc.columns])

    # Update the layout
    fig.update_layout(
        barmode='stack',
        title='Renewable Energy Consumption by Region in {}'.format(year),
        xaxis_title='Region',
        yaxis_title='Renewable Energy Consumption (%)',
        hovermode='closest',
        hoverlabel=dict(bgcolor="white", font_size=16),
        legend=dict(
            traceorder='normal',
            itemclick=False,
            title='Energy Type',
            font=dict(size=14),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=50, r=50, t=100, b=50),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color='white'), ##all font
    )

    return fig

#Creates top 10 renewables consumption per country and with stacked bars - it is possible to select some variables
def top_10_renewables(year, energies=None):
    energy_columns = ['other_renewable_consumption', 'solar_consumption', 'wind_consumption', 'hydro_consumption', 'biofuel_consumption']
    if energies==None:
        energies=energy_columns
    renewables = data[['country', 'region', 'year'] + energy_columns]
    renewables = renewables[renewables['country']!='World']
    renewables_year = renewables[renewables['year'] == year][['country'] + energy_columns]
    # Calculate the total consumption for each country
    renewables_year_totals = renewables_year.groupby('country').sum()
    # Filter by energies list
    renewables_year_totals = renewables_year_totals[energies]
    # Sort values in descending order
    renewables_year_totals = renewables_year_totals.loc[renewables_year_totals[energies].sum(axis=1).sort_values(ascending=False).index, energies]

    # Get top 10 countries
    top_10_df = renewables_year_totals.iloc[:10,:]
    # Reverse the order of the data frame so that the largest bar appears on top
    top_10_df = top_10_df.iloc[::-1]
   
    # Set colors for the different types of energy
    colors = {'other_renewable_consumption': '#0066CC',
            'solar_consumption': '#FFD700',
            'wind_consumption': '#92C6FF',
            'hydro_consumption': '#003366',
            'biofuel_consumption': '#008000'}

    # Create the horizontal bar chart
    fig = go.Figure(data=[go.Bar(
        y=top_10_df.index,
        x=top_10_df[col],
        name=col.split('_')[0].capitalize(),
        marker_color=colors[col],
        orientation='h',
        customdata=[[top_10_df.loc[country].sum()] * len(top_10_df.columns) for country in top_10_df.index],
        hovertemplate="<b>Total Renewables Consumption:</b> %{customdata[0]:.2f} TWh<br>" +
                    #   "<b>%{x:.2f} TWh</b> " + col.split('_')[0].capitalize() +" Consumption in %{y}<extra></extra>"
                      "<b>" + col.split('_')[0].capitalize() + " Consumption: </b>" + "%{x:.2f} TWh<extra></extra>"
    ) for col in top_10_df.columns])

    # Update the layout
    fig.update_layout(
        barmode='stack',
        title='Top 10 Countries for Renewable Energy Consumption in {}'.format(year),
        xaxis_title='Renewables Energy Consumption (terawatt-hours)',
        yaxis_title='Country',
        hovermode='closest',
        hoverlabel=dict(font_size=12),
        legend=dict(
            traceorder='normal',
            itemclick=False,
            title='Energy Type',
            font=dict(size=14),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=200, r=50, t=100, b=50),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color='white'),
    )

    return fig







################### COMPONENTS #######################
# Define the slider marks for every 10 years
slider_marks = {str(year): {'label': str(year), 'style': {'writing-mode': 'horizontal-tb', 'font-size': '16px'}} for year in range(1965, 2020, 5)}
slider_marks['2019'] = {'label': '2019', 'style': {'writing-mode': 'horizontal-tb', 'font-size': '16px'}}
# Create initial plots for 1965
fig_oil_consu_plot = fig_world_consu('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_oil_consu_slider = fig_consu_slider('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_oil_top_10 = fig_top10_graph('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_oil_choropleth = create_choropleth_map('oil_consumption', 'Oil', 1965)

fig_coal_consu_plot = fig_world_consu('coal_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_coal_consu_slider = fig_consu_slider('coal_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_coal_top_10 = fig_top10_graph('coal_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_coal_choropleth = create_choropleth_map('coal_consumption', 'Oil', 1965)

fig_ren_consu_plot = fig_world_consu('renewables_consumption', 'Renewables', 'Renewables Consumption (terawatt-hours)', 1965)
fig_ren_stacked = stacked_renewables(1965)
fig_ren_top_10 = top_10_renewables(1965)

######################################################

# Create the app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.Img(src='https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/logo.png', height='80px', style={'float': 'left', 'margin':0}),
        html.H1('Energy Consumption Dashboard', style={'textAlign': 'center', 'margin': 'auto', 'color': 'white'}),
        
    ], id='header'),

    dcc.Tabs(id="energy_tabs", value='tab-1', children=[
        dcc.Tab(id='oil-tab', label='Oil', value='tab-1', children=[
            html.Div([
                html.Div([
                    dcc.Graph(id='fig_oil_top_10', figure=fig_oil_top_10),
                
                    dcc.Graph(id='fig_oil_choropleth', figure=fig_oil_choropleth),
                ], className="row"),
                html.Div([
                    dcc.Slider(id='year-slider', min=1965, max=2019, value=1965, marks=slider_marks, step=1, tooltip={'always_visible': True, 'placement': 'top'})
                ], className="row-slider"),
                html.Div([
                    dcc.Graph(id='fig_oil_consu_plot', figure=fig_oil_consu_plot),
                    dcc.Graph(id='fig_oil_consu_slider', figure=fig_oil_consu_slider),
                ], className="row")
            ], style={"width": "100%"})
        ], selected_style={'background-color': "#5F9EA0", 'border': '3px solid black', 'font-weight': 'bold'}),
        dcc.Tab(label='Coal', value='tab-2', children=[
           html.Div([
                html.Div([
                    dcc.Graph(id='fig_coal_top_10', figure=fig_coal_top_10),
                
                    dcc.Graph(id='fig_coal_choropleth', figure=fig_coal_choropleth),
                ], className="row"),
                html.Div([
                    dcc.Slider(id='year-slider2', min=1965, max=2019, value=1965, marks=slider_marks, step=1, tooltip={'always_visible': True, 'placement': 'top'})
                ], className="row-slider"),
                html.Div([
                    dcc.Graph(id='fig_coal_consu_plot', figure=fig_coal_consu_plot),
                    dcc.Graph(id='fig_coal_consu_slider', figure=fig_coal_consu_slider),
                ], className="row")
            ], style={"width": "100%"})
        ], selected_style={'background-color': "#5F9EA0", 'border': '3px solid black', 'font-weight': 'bold'}),
        dcc.Tab(label='Renewables', value='tab-3', children=[
           html.Div([
                html.Div([
    
                    dcc.Dropdown(id='energy_dropdown', options=[
                                                    {
                                                        'label': html.Span(['Hydro'], style={'background-color': '#003366', 'font-size': 20}),
                                                        'value':'hydro_consumption'
                                                    },
                                                    {'label': html.Span(['Solar'], style={'background-color': '#FFD700', 'font-size': 20}),
                                                        'value':'solar_consumption'
                                                     },
                                                     {'label': html.Span(['Biofuel'], style={'background-color': '#008000', 'font-size': 20}),
                                                        'value':'biofuel_consumption'
                                                     },
                                                     {'label': html.Span(['Wind'], style={'background-color': '#92C6FF', 'font-size': 20}),
                                                        'value':'wind_consumption'
                                                     },
                                                     {'label': html.Span(['Other Renewables'], style={'background-color': '#0066CC', 'font-size': 20}),
                                                        'value':'other_renewable_consumption'
                                                     },

                                                ]
                                    
                                    , multi=True
                                    , style={'backgroundColor': '#283142', 'font-size': 20, 'color':'white'}
                                    , clearable=False
                                    , placeholder="Select energy types"),


                ], className="row-drop"),
                html.Div([
                    dcc.Graph(id='fig_stacked_renew', figure=fig_ren_stacked),

                    dcc.Graph(id='fig_ren_consu_plot', figure=fig_ren_consu_plot),
                ], className="row"),
                html.Div([
                    dcc.Slider(id='year-slider3', min=1965, max=2019, value=1965, marks=slider_marks, step=1, tooltip={'always_visible': True, 'placement': 'top'})
                ], className="row-slider"),
                html.Div([
                    dcc.Graph(id='fig_ren_top_10', figure=fig_ren_top_10),

                ], className="row")
            ], style={"width": "100%"})
        ], selected_style={'background-color': "#5F9EA0", 'border': '3px solid black', 'font-weight': 'bold'}),

        dcc.Tab(label='Comparison', value='tab-4', selected_style={'background-color': "#5F9EA0", 'border': '3px solid black', 'font-weight': 'bold'})
    ]),
    html.Div(id='tabs-content-example-graph'),
    html.Footer([
 html.Img(src='https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/logo-preto.png', height='80px', style={'float': 'left', 'margin':0}),
                 html.H1([html.B('Data source: '), 'https://www.kaggle.com/datasets/pralabhpoudel/world-energy-consumption']),
        html.H1([html.B('Authors: '), 'Guilherme Henriques - Henrique Marques - Vasco Bargas'])
    ])
])


#Callback oil tab
@app.callback([
    dash.dependencies.Output('fig_oil_consu_plot', 'figure'),
    dash.dependencies.Output('fig_oil_consu_slider', 'figure'),
    dash.dependencies.Output('fig_oil_top_10', 'figure'),
    dash.dependencies.Output('fig_oil_choropleth', 'figure'),
],
[
    dash.dependencies.Input('energy_tabs', 'value'),
    dash.dependencies.Input('year-slider', 'value'),
])
def render_content(tab, year):
    empty_fig = go.Figure()
    empty_fig.update_layout(height=400, margin={'l': 0, 'b': 0, 'r': 0, 't': 0})
    if tab == 'tab-1':
        fig1 = fig_world_consu('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', year)
        fig2 = fig_consu_slider('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', year)
        fig3 = fig_top10_graph('oil_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', year)
        fig4 = create_choropleth_map('oil_consumption', 'Oil', year)
        return fig1, fig2, fig3, fig4
    else:
        return empty_fig, empty_fig, empty_fig, empty_fig


# Callback coal tab
@app.callback([
    dash.dependencies.Output('fig_coal_consu_plot', 'figure'),
    dash.dependencies.Output('fig_coal_consu_slider', 'figure'),
    dash.dependencies.Output('fig_coal_top_10', 'figure'),
    dash.dependencies.Output('fig_coal_choropleth', 'figure'),
],
[
    dash.dependencies.Input('energy_tabs', 'value'),
    dash.dependencies.Input('year-slider2', 'value'),
])
def render_content(tab, year2):
    empty_fig = go.Figure()
    empty_fig.update_layout(height=400, margin={'l': 0, 'b': 0, 'r': 0, 't': 0})
    
    if tab == 'tab-2':
        # return default values for coal-related figures
        fig1 = fig_world_consu('coal_consumption', 'Coal', 'Coal Consumption (terawatt-hours)', year2)
        fig2 = fig_consu_slider('coal_consumption', 'Oil', 'Coal Consumption (terawatt-hours)', year2)
        fig3 = fig_top10_graph('coal_consumption', 'Coal', 'Coal Consumption (terawatt-hours)', year2)
        fig4 = create_choropleth_map('coal_consumption', 'Coal', year2)
        return  fig1, fig2, fig3, fig4
    else:
        return empty_fig, empty_fig, empty_fig, empty_fig
    


# Callback ren tab
@app.callback([
    dash.dependencies.Output('fig_ren_consu_plot', 'figure'),
    dash.dependencies.Output('fig_ren_top_10', 'figure'),
    dash.dependencies.Output('fig_stacked_renew', 'figure'),
],
[
    dash.dependencies.Input('energy_tabs', 'value'),
    dash.dependencies.Input('year-slider3', 'value'),
    dash.dependencies.Input('energy_dropdown', 'value'),
])
def render_content(tab, year2, energy):
    empty_fig = go.Figure()
    empty_fig.update_layout(height=400, margin={'l': 0, 'b': 0, 'r': 0, 't': 0})

    
    if tab == 'tab-3':
        if energy!=None:
            if len(energy)==0:
                energy=None
        # return default values for coal-related figures
        fig1 = fig_world_consu('renewables_consumption', 'Renewables', 'Renewables Consumption (terawatt-hours)', year2)
        fig2 = stacked_renewables(year2, energy)
        fig3 = top_10_renewables(year2, energy)
        return  fig1, fig2, fig3
    else:
        return empty_fig, empty_fig, empty_fig
 


if __name__ == '__main__':
    app.run_server(debug=True)
