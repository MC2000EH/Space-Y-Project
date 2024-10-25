# Import required libraries
import pandas as pd
import dash
from dash import html, dcc  # Updated import paths
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for selecting launch site
    html.Div(dcc.Dropdown(id='site_dropdown',
                          options=[
                              {'label': 'All Sites', 'value': 'ALL'},
                              {'label': 'Site 1: CCAFS LC-40', 'value': 'CCAFS LC-40'},
                              {'label': 'Site 2: VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                              {'label': 'Site 3: KSC LC-39A', 'value': 'KSC LC-39A'},
                              {'label': 'Site 4: CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                          ],
                          placeholder="Select launch site",
                          searchable=True)),
    html.Br(),

    # Pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Payload range slider
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),  # Used correct min/max values from dataframe

    # Scatter plot for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site_dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class',  # You might want to adjust 'values' field depending on your data
                     names='Launch Site',
                     title='Launch Success Rate for All Sites')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        success_count = filtered_df['class'].value_counts().reset_index()
        success_count.columns = ['class', 'count']
        fig = px.pie(success_count, values='count',  # Ensure 'class' is correct here
                     names='class',
                     title=f'Launch Success Rate for Site {entered_site}')
    return fig

# Callback for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site_dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    filtered_df2 = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                             (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if entered_site == 'ALL':
        fig = px.scatter(filtered_df2, x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites')
    else:
        filtered_df2 = filtered_df2[filtered_df2['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df2, x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {entered_site}')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
