import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Load the data
data = pd.read_csv(
    'https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/World%20Energy%20Consumption.csv')

continents = pd.read_csv(
    'https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/country_continent_map.csv')



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
def create_choropleth_map(variable, energy_type, year, renewables):
    if renewables==True:
        if variable==None:
            variable = 'renewables_consumption'
            energy_type = 'Renewables'
        else:
            energy_type=variable[0].split('_')[0].capitalize()
            variable=variable[0]
    

    # df for oil_consumption plots
    consumption_df = data[data[variable].notna()][[variable, 'year', 'iso_code', 'country']]

    # Filter data for the given year
    oil_data_year = consumption_df[consumption_df["year"] == year]

    # Define the choropleth map
    fig = go.Figure(go.Choropleth(
        locations=oil_data_year["iso_code"],
        z=oil_data_year[variable],
        colorscale="YlOrRd",
        zmin=oil_data_year[(oil_data_year['year']==year) & (oil_data_year['country']!='World')][variable].min(),
        zmax=oil_data_year[(oil_data_year['year']==year) & (oil_data_year['country']!='World')][variable].sort_values(ascending=False).iloc[1],
        marker_line_width=0.5,
        marker_line_color="white",
        text=oil_data_year["country"],
        hovertemplate="<b>%{text}</b><br>" + energy_type + " Consumption: %{z:.2f} TWh",
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
        margin={"l": 0, "r": 30, "t": 40, "b": 0},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color='white'), ##all font
        # height=800
    )
    
    # Update the title with the current year
    fig.update_layout(title={"text": energy_type + " Consumption per Country in {}".format(year)})

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
       title={
        'text': 'Renewable Energy Consumption by Region in {}'.format(year),
        'x': 0.5 # set title_x to 0.5 to center the title
    },
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
        margin=dict(l=150, r=0, t=100, b=0),
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
        margin=dict(l=0, r=0, t=100, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color='white'),
    )

    return fig

#Creates Gauge indicator
def plot_gauge_chart(year, variable, energy_type, color, country):
    
    data['non_renewables_share_elec']=data[['nuclear_share_elec', 'oil_share_elec', 'coal_share_elec', 'gas_share_elec']].sum(axis=1)
    
    # Filter data for specified year
    data1 = data[(data['year'] == year)& (data['country']==country)]

    fig = go.Figure()

    fig.update_layout(
        title=energy_type + ' pct. of Electricity Prod.',
        font=dict(size=9, color='white'),
        width=300,
        height=250,
        showlegend=False,  # remove legend on the axis
        title_y=0.7,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=data1[variable].iloc[0],
        gauge=dict(
            axis=dict(range=[None, 100], tickmode='array', tickvals=[]),
            bar=dict(color=color),
            bgcolor = 'white',
            borderwidth = 0,
            bordercolor = 'gray',
            steps=[
                dict(range=[0, data1[variable].iloc[0]], color=color)
            ],
        ),
        domain=dict(x=[0, 1], y=[0, 1]),
        number=dict(suffix="%", font=dict(color=color, size=25))  # increase size of main value
    ))

    return fig

#Create Sunburst
data['non_renewables_consumption']=data[['nuclear_consumption', 'oil_consumption', 'coal_consumption', 'gas_consumption']].sum(axis=1)
def sunburst_plot(year, country):
    # Filter data for 'World'
    world_data = data[(data['year'] == year) & (data['country'] == country)]

    # Create labels and parents for the sunburst plot
    labels = ['Renewables', 'Non-Renewables',  'Hydro', 'Solar', 'Biofuel', 'Others', 'Wind', 
            'Coal', 'Oil', 'Gas', 'Nuclear', 'Fossil']
    parents = ['','',  'Renewables', 'Renewables', 'Renewables', 'Renewables', 'Renewables',
                'Non-Renewables', 'Non-Renewables', 'Non-Renewables', 'Non-Renewables']

    # Create values for the sunburst plot
    values = [world_data['renewables_consumption'].values[0], 
            world_data['non_renewables_consumption'].values[0],
            world_data['hydro_consumption'].values[0], 
            world_data['solar_consumption'].values[0],
            world_data['biofuel_consumption'].values[0],
            world_data['other_renewable_consumption'].values[0],
            world_data['wind_consumption'].values[0],
            world_data['coal_consumption'].values[0], 
            world_data['oil_consumption'].values[0],
            world_data['gas_consumption'].values[0], 
            world_data['nuclear_consumption'].values[0]]

    # Apply log transformation to values for better visualization
    # values = np.log(values)
    # Create a list of colors for each label
    colors = ['#7FFF00', '#A52A2A', '#7FFF00', '#7FFF00', '#7FFF00', '#7FFF00', '#7FFF00',
            '#A52A2A', '#A52A2A', '#A52A2A', '#A52A2A', '#A52A2A']

    # Construct the sunburst plot with modified marker attribute
    sunburst_data = dict(type='sunburst',
                        labels=labels, 
                        parents=parents, 
                        values=values,
                        branchvalues='total',
                        marker=dict(colors=colors, line=dict(width=2, color='white')))


    sunburst_layout = dict(margin=dict(t=50, l=0, r=0, b=0))

    sunburst = go.Figure(data=sunburst_data, layout=sunburst_layout)

    # Set title and show the plot
    sunburst.update_layout(title= country + ' Energy Consumption in ' + str(year) + ' by Source in TWh', 
                           font=dict(size=12, color='white'),
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",)
    return sunburst

def create_scatter(year):
   # filter data for the year 2019
    data_scatter = data[(data['year'] == year) & (data['country'] != 'World')]

    # sort data by non_renewables_consumption in descending order and select top 10 rows
    data_top10 = data_scatter.sort_values('non_renewables_consumption', ascending=False)

    # create a dictionary to map region to color
    color_dict = {'Africa': '#008080', # teal
              'North America': '#FFA07A', # light salmon
              'Asia': '#FFD700', # gold
              'Europe': '#EE82EE', # violet
              'Oceania': '#00FFFF', # cyan
              'South America': '#32CD32'} # lime green
    # create an empty list to store the traces
    traces = []

    # iterate over the regions and create a trace for each one
    for region in color_dict.keys():
        # filter the data by region
        data_region = data_top10[data_top10['region'] == region]
        # create a scatter trace for the region
        trace = go.Scatter(
            x=np.log(data_region['renewables_consumption']),
            y=np.log(data_region['non_renewables_consumption']),
            mode='markers',
            marker=dict(
                size=10,
                color=color_dict[region],
            ),
            name=region, # set the name for the legend
            text=data_region['country'],
        )
        # append the trace to the list
        traces.append(trace)

    # create the figure with all the traces
    fig = go.Figure(data=traces)

    fig.update_layout(
        title='Renewables vs Non-Renewables Consumption in ' + str(year),
        xaxis_title='Renewables Consumption',
        yaxis_title='Non-Renewables Consumption',
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12, color='white'),
        xaxis_range=[ 1, np.log(data_top10[data_top10['year']==year]['renewables_consumption'].max())+0.5],
        yaxis_range=[np.log(data_top10[data_top10['year']==year]['non_renewables_consumption'].min() or 1), np.log(data_top10['non_renewables_consumption'][data_top10['year']==2019].max())+0.5],
        legend=dict(
            orientation='h', # set the legend orientation to horizontal
            yanchor='bottom', # set the anchor for the y position of the legend
            y=1.02, # adjust the y position of the legend
            xanchor='right', # set the anchor for the x position of the legend
            x=1, # adjust the x position of the legend
        ),
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
fig_oil_choropleth = create_choropleth_map('oil_consumption', 'Oil', 1965, False)

fig_coal_consu_plot = fig_world_consu('coal_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_coal_consu_slider = fig_consu_slider('coal_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_coal_top_10 = fig_top10_graph('coal_consumption', 'Oil', 'Oil Consumption (terawatt-hours)', 1965)
fig_coal_choropleth = create_choropleth_map('coal_consumption', 'Oil', 1965, False)

fig_ren_consu_plot = fig_world_consu('renewables_consumption', 'Renewables', 'Renewables Consumption (terawatt-hours)', 1965)
fig_ren_stacked = stacked_renewables(1965)
fig_ren_top_10 = top_10_renewables(1965)
fig_ren_choropleth = create_choropleth_map(None, None, 1965, True)

#Define the slider from 1985 to 2019
slider_marks_1985 = {str(year): {'label': str(year), 'style': {'writing-mode': 'horizontal-tb', 'font-size': '16px'}} for year in range(1985, 2020, 5)}
slider_marks_1985['2019'] = {'label': '2019', 'style': {'writing-mode': 'horizontal-tb', 'font-size': '16px'}}


fig_gauge_ren = plot_gauge_chart(1985, 'renewables_share_elec', 'Renewables', '#7FFF00', 'World')
fig_gauge_non_ren = plot_gauge_chart(1985, 'non_renewables_share_elec', 'Non Renewables', '#A52A2A', 'World')
fig_sunburst = sunburst_plot(1985, 'World')  
fig_scatter = create_scatter(1985)

# Extract unique country names from the DataFrame to dropdown
country_options = [{'label': country, 'value': country} for country in
                    data[data[['renewables_consumption', 'non_renewables_consumption', 'hydro_consumption', 'solar_consumption', 'biofuel_consumption', 'wind_consumption', 'coal_consumption', 'oil_consumption', 'gas_consumption', 'nuclear_consumption', 'fossil_fuel_consumption']].notnull()
                         .all(axis=1)]['country'].unique()]

######################################################

# Create the app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.Img(src='https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/logo.png', height='80px', style={'float': 'left', 'margin':0}),
        html.H1('Energy Consumption Dashboard'),
        # html.Br(),
        html.H2('Visualize and compare energy consumption across oil, coal, and renewables'),
        
    ], id='header'),

    dcc.Tabs(id="energy_tabs", value='tab-1', children=[
        dcc.Tab(id='oil-tab',label='Oil',value='tab-1',children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Br(),
                            html.Div(id="tabs-intro", className="tabs-intro", children=[
                                'Explore the global ', html.Strong('consumption of oil '),
                                'with our choropleth map and top 10 countries plot provide a comprehensive view of oil consumption around the world.',
                                html.P('Use the slider below the plots to see how consumption has changed over time from 1965 to 2019.'),    
                                html.P('Gain insights into the most oil-hungry countries and their trends over time.')], 
                                     ),

                        ],
                        className='row-tabs-intro' ),
                    html.Br(),
                    html.Div(
                        children=[
                            dcc.Graph(id='fig_oil_choropleth', figure=fig_oil_choropleth),
                            dcc.Graph(id='fig_oil_top_10', figure=fig_oil_top_10)
                        ],
                        className='row', style={'background-color': '#3c4a63', 'padding': '10px'}
                    ),
                    html.Br(),
                    html.Div(
                        children=[
                            dcc.Slider(
                                id='year-slider',
                                min=1965,
                                max=2019,
                                value=1965,
                                marks=slider_marks,
                                step=1,
                                tooltip={'always_visible': True, 'placement': 'top'},
                                updatemode='drag'
                            )
                        ],
                        className='row-slider'),
                        
                    html.Div(
                        children=[
                            html.Br(),
                            html.Div( className="tabs-intro", children=[
                                'Moving from a country-level analysis to a global perspective, we present our next set of plots that showcase the worldwide consumption of oil.'], 
                                     ),

                        ],
                        className='row-tabs-intro-final' ),
                    html.Div(
                        children=[
                            dcc.Graph(id='fig_oil_consu_plot',figure=fig_oil_consu_plot),
                            dcc.Graph(id='fig_oil_consu_slider', figure=fig_oil_consu_slider)
                        ],
                        className='row', style={'background-color': '#3c4a63','padding': '10px'}
                    )
                ],
                className='main_row'
            )
            
        ],selected_style={'background-color': '#5F9EA0', 'border': '1px solid black','font-weight': 'bold' },
        style={'background-color': '#5F9EA0','filter': 'brightness(70%)'}
        ),
        dcc.Tab(id='coal-tab',label='Coal',value='tab-2',children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Br(),
                            html.Div( className="tabs-intro", children=[
                                'Explore the global ', html.Strong('consumption of coal '),
                                'with our choropleth map and top 10 countries plot provide a comprehensive view of coal consumption around the world.',
                                html.P('Use the slider below the plots to see how consumption has changed over time from 1965 to 2019.'),    
                                html.P('Gain insights into the most coal-hungry countries and their trends over time.')], 
                                     ),

                        ],
                        className='row-tabs-intro' ),
                    html.Br(),
                    html.Div(
                        children=[
                            dcc.Graph(id='fig_coal_choropleth', figure=fig_coal_choropleth),
                            dcc.Graph(id='fig_coal_top_10', figure=fig_coal_top_10)
                        ],
                        className='row', style={'background-color': '#3c4a63', 'padding': '10px'}
                    ),
                    html.Br(),
                    html.Div(
                        children=[
                            dcc.Slider(
                                id='year-slider2',
                                min=1965,
                                max=2019,
                                value=1965,
                                marks=slider_marks,
                                step=1,
                                tooltip={'always_visible': True, 'placement': 'top'},
                                updatemode='drag'
                            )
                        ],
                        className='row-slider'),
                    html.Div(
                        children=[
                            html.Br(),
                            html.Div( className="tabs-intro", children=[
                                'Moving from a country-level analysis to a global perspective, we present our next set of plots that showcase the worldwide consumption of coal.'], 
                                     ),

                        ],
                        className='row-tabs-intro-final' ),
                        
                    html.Div(
                        children=[
                            dcc.Graph(id='fig_coal_consu_plot',figure=fig_coal_consu_plot),
                            dcc.Graph(id='fig_coal_consu_slider', figure=fig_coal_consu_slider)
                        ],
                        className='row', style={'background-color': '#3c4a63','padding': '10px'}
                    )
                ],
                className='main_row'
            )
            
        ],selected_style={'background-color': '#5F9EA0', 'border': '1px solid black','font-weight': 'bold' },
        style={'background-color': '#5F9EA0','filter': 'brightness(70%)'}
        ),
        dcc.Tab(label='Renewables', value='tab-3',children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div( className="tabs-intro", children=[
                                'Explore the global ', html.Strong('consumption of renewable energy '),
                                'with our .......................',
                                html.P('Use the slider ..... FALAR DA SELECAO DE ENERGIAS............1965 to 2019.'),    
                                html.P('GSDFSDFSDFS.')], 
                                     ),
                            html.Div([
    
                                dcc.Dropdown(id='energy_dropdown', options=[
                                                    {
                                                        'label': html.Span(['Hydro']),
                                                        'value':'hydro_consumption'
                                                    },
                                                    {'label': html.Span(['Solar']),
                                                        'value':'solar_consumption'
                                                     },
                                                     {'label': html.Span(['Biofuel']),
                                                        'value':'biofuel_consumption'
                                                     },
                                                     {'label': html.Span(['Wind']),
                                                        'value':'wind_consumption'
                                                     },
                                                     {'label': html.Span(['Other Renewables']),
                                                        'value':'other_renewable_consumption'
                                                     },

                                                ]
                                    
                                    , multi=True
                                    , style={'backgroundColor': '#283142', 'font-size': 20, 'color':'white'}
                                    , clearable=False
                                    , placeholder="Select energy types"
                                    ),
                                ], className="row-drop"),

                        ],
                        className='row-tabs-intro' ),
                            html.Br(),
                    html.Br(),
                    html.Div(
                        children=[
                            dcc.Graph(id='fig_ren_choropleth', figure=fig_ren_choropleth),
                            # html.Div('ola'),
                            dcc.Graph(id='fig_ren_top_10', figure=fig_ren_top_10),
                        ],
                        className='row', style={'background-color': '#3c4a63', 'padding': '10px'}
                    ),
                    html.Br(),
                    html.Div(
                        children=[
                            dcc.Slider(
                                id='year-slider3',
                                min=1965,
                                max=2019,
                                value=1965,
                                marks=slider_marks,
                                step=1,
                                tooltip={'always_visible': True, 'placement': 'top'},
                                updatemode='drag'
                            )
                        ],
                        className='row-slider'),
                    html.Div(
                        children=[
                            html.Br(),
                            html.Div( className="tabs-intro", children=[
                                'Moving from a country-level analysis to a global perspective, we present our next set of plots that showcase the worldwide consumption of coal.'], 
                                     ),

                        ],
                        className='row-tabs-intro-final' ),
                        
                    html.Div(
                        children=[
                            dcc.Graph(id='fig_ren_consu_plot', figure=fig_ren_consu_plot),
                            dcc.Graph(id='fig_stacked_renew', figure=fig_ren_stacked),

                        ],
                        className='row', style={'background-color': '#3c4a63','padding': '10px'}
                    )
                ],
                className='main_row'
            )
            
        ],selected_style={'background-color': '#5F9EA0', 'border': '1px solid black','font-weight': 'bold' },
        style={'background-color': '#5F9EA0','filter': 'brightness(70%)'}
        ),

        dcc.Tab(label='Comparison', value='tab-4',children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Br(),
                            html.Div( className="tabs-intro", children=[
                                'Explore the global ', html.Strong('consumption of coal '),
                                'with sdfsdfsdfsdf......................',
                                html.P('Use the slider below the plots to ................ 1985 to 2019.'),    
                                html.P('Gain insights into TRTRTTTTTTTTTTTTTTT.')], 
                                     ),
                           html.Div([
                    dcc.Dropdown(
                        id='country_dropdown',
                        options=country_options,
                        value='World',
                    )
                ], className='row-drop'),

                        ],
                        className='row-tabs-intro' ),
                    html.Div([
                    html.Div([
                        html.Div('EXPLAIN THE GAUGE CHARTS...........', style={'color': 'white'}),
                        html.Div([
                            dcc.Graph(id='fig_gauge_ren',
                                      figure=fig_gauge_ren),
                            dcc.Graph(id='fig_gauge_non_ren',
                                      figure=fig_gauge_non_ren),
                        ], className='row'),
                        dcc.Graph(id='fig_scatter', figure=fig_scatter),
                    ], className='six columns'),
                    html.Div([
                        dcc.Graph(id='fig_sunburst', figure=fig_sunburst),
                    ], className='six columns'),
                ], className='row'),
                    html.Div(
                        children=[
                            dcc.Slider(id='year-slider4', min=1985, max=2019, value=1985, marks=slider_marks_1985,
                               step=1, tooltip={'always_visible': True, 'placement': 'top'}, updatemode='drag')
                            
                        ],
                        className='row-slider'),
                    
                ],
                className='main_row'
            )
            
        ],selected_style={'background-color': '#5F9EA0', 'border': '1px solid black','font-weight': 'bold' },
        style={'background-color': '#5F9EA0','filter': 'brightness(70%)'}
        ),
    ]),
    html.Div(id='tabs-content-example-graph'),
    html.Footer([
 html.Img(src='https://raw.githubusercontent.com/henrymmarques/DataVizProj/master/logo-preto.png', height='80px', style={'float': 'left', 'margin':0}),
        html.H1([html.B('Authors: '), 'Guilherme Henriques - Henrique Marques - Vasco Bargas']),
                 html.H1([html.B('Data source: '), 'https://www.kaggle.com/datasets/pralabhpoudel/world-energy-consumption']),
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
        fig4 = create_choropleth_map('oil_consumption', 'Oil', year, False)
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
        fig4 = create_choropleth_map('coal_consumption', 'Coal', year2, False)
        return  fig1, fig2, fig3, fig4
    else:
        return empty_fig, empty_fig, empty_fig, empty_fig
    


# Callback ren tab
@app.callback([
    dash.dependencies.Output('fig_ren_consu_plot', 'figure'),
    dash.dependencies.Output('fig_ren_top_10', 'figure'),
    dash.dependencies.Output('fig_stacked_renew', 'figure'),
    dash.dependencies.Output('fig_ren_choropleth', 'figure'),
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
        fig4 = create_choropleth_map(energy, energy, year2, True)
        return  fig1, fig2, fig3, fig4
    else:
        return empty_fig, empty_fig, empty_fig, empty_fig


# Callback comparison tab
@app.callback([
    dash.dependencies.Output('fig_gauge_ren', 'figure'),
    dash.dependencies.Output('fig_gauge_non_ren', 'figure'),
    dash.dependencies.Output('fig_sunburst', 'figure'),
    dash.dependencies.Output('fig_scatter', 'figure'),
],
[
    dash.dependencies.Input('energy_tabs', 'value'),
    dash.dependencies.Input('year-slider4', 'value'),
    dash.dependencies.Input('country_dropdown', 'value'),
])
def render_content(tab, year2, country):
    empty_fig = go.Figure()
    empty_fig.update_layout(height=400, margin={'l': 0, 'b': 0, 'r': 0, 't': 0})

    if tab == 'tab-4':
        if country==None:
            country='World'
        fig1 = plot_gauge_chart(year2, 'renewables_share_elec', 'Renewables', '#7FFF00', country)
        fig2 = plot_gauge_chart(year2, 'non_renewables_share_elec', 'Non Renewables', '#A52A2A', country)
        fig3 = sunburst_plot(year2, country)
        fig4 = create_scatter(year2)
        return  fig1, fig2, fig3, fig4
    else:
        return empty_fig, empty_fig, empty_fig, empty_fig
 


if __name__ == '__main__':
    app.run_server(debug=True)
