import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Dataset Processing

data = pd.read_csv('World Energy Consumption.csv')
continents = pd.read_csv('continents2.csv')
continents = continents[['name', 'alpha-3', 'region', 'sub-region']]
regions = data.iso_code.replace(continents.set_index('alpha-3')['region'])
data['region']=regions
data = data[data['iso_code'].notna()]
sub_regions = data.iso_code.replace(continents.set_index('alpha-3')['sub-region'])
data['sub_region']=sub_regions

oil_consumption_df=data[data['oil_consumption'].notna()][['oil_consumption', 'year', 'iso_code', 'country', 'region', 'sub_region' ]]



# Requirements for the dash core components


year_slider = dcc.RangeSlider(
        id='year_slider',
        min=1990,
        max=2014,
        value=[1990, 2014],
        marks={'1990': 'Year 1990',
               '1995': 'Year 1995',
               '2000': 'Year 2000',
               '2005': 'Year 2005',
               '2010': 'Year 2010',
               '2014': 'Year 2014'},
        step=1
    )

# The app itself

app = dash.Dash(__name__)

app.layout = html.Div([

   

    html.Br(),

    dcc.Graph(id='graph_example'),

    html.Br(),
    year_slider

])


@app.callback(
    Output('graph_example', 'figure'),
    [Input('country_drop', 'value'),
     Input('gas_radio', 'value'),

     Input('year_slider', 'value')]
)
def update_graph(countries, gas, year):
        
        
    # filter the data
    world_data = oil_consumption_df[oil_consumption_df['country'] == 'World']

    # create the bar chart trace
    trace = go.Bar(
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

    # create the layout
    layout = go.Layout(
        title='WorldWide Oil Consumption by Year',
        xaxis=dict(
            title='Year',
            tickmode='linear',
            dtick=1,
            tickangle=270
        ),
        yaxis=dict(
            title='Oil Consumption (terawatt-hours)'
        ),
        plot_bgcolor='white',
        hoverlabel=dict()
    )

    # create the figure
    fig = go.Figure(data=[trace], layout=layout)

    # update the text font size
    fig.update_traces(textfont_size=12)





    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
