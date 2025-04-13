from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def create_renewable_dashboard(dataset, color_palette):
    #filter without consumption/verification/sold
    renewable = dataset[~dataset['Source'].str.contains('Consumption|Verification|Sold', case=False, na=False)]
    
    #filter options for years and sources 
    years = sorted(renewable['Fiscal Year'].unique())
    sources = sorted(renewable['Source'].unique())
    
    # Get all states
    all_states = sorted(renewable['State'].unique())
    
    # Calculate the top 10 states by number of renewable energy initiatives
    state_counts = renewable.groupby('State').size().reset_index(name='count')
    state_counts = state_counts.sort_values('count', ascending=False)
    top_10_states = state_counts.head(10)['State'].tolist()
    
    #create the app for dashboard 
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 
    server = app.server

    app.layout = dbc.Container([
        html.H1("Renewable Energy Dashboard", className="mt-4 mb-4"),
        dbc.Row([
            dbc.Col([
                html.H4("Filters"),
                dbc.Card([
                    dbc.CardBody([
                        html.P("Select Year Range:"),
                        dcc.RangeSlider(
                            id='year-slider',
                            min=min(years),
                            max=max(years),
                            value=[min(years), max(years)],
                            marks={int(year): str(year) for year in years}, #all years 
                            step=None
                        ),
                        html.Br(),
                        html.P("Select States:"),
                        dcc.Dropdown(
                            id='state-selector',
                            options=[{'label': state, 'value': state} for state in all_states],
                            value=top_10_states, # top 10 states by count
                            multi=True
                        ),
                        html.Br(),
                        html.P("Select Energy Sources:"),
                        dcc.Dropdown(
                            id='source-selector',
                            options=[{'label': source, 'value': source} for source in sources],
                            value=sources, #all sources 
                            multi=True
                        )
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Renewable Energy Sources by State"),
                dcc.Graph(id='state-chart')
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Renewable Energy Sources Over Time"),
                dcc.Graph(id='time-chart')
            ], width=12)
        ])
    ], fluid=True)
    
    @app.callback(
        [Output('state-chart', 'figure'),
         Output('time-chart', 'figure')],
        [Input('year-slider', 'value'),
         Input('state-selector', 'value'),
         Input('source-selector', 'value')]
    )
    
    def update_graphs(years_range, selected_states, selected_sources):
        #combination filter 
        filtered_data = renewable[
            (renewable['Fiscal Year'] >= years_range[0]) & 
            (renewable['Fiscal Year'] <= years_range[1]) &
            (renewable['State'].isin(selected_states)) &
            (renewable['Source'].isin(selected_sources))
        ]
        
        state_chart = px.bar(
            filtered_data.groupby(['State', 'Source']).size().reset_index(name='Count'),
            x='Count',
            y='State',
            color='Source',
            color_discrete_sequence=color_palette[:len(selected_sources)],
            orientation='h',
            title=f'Renewable Energy by State',
            labels={'Count': 'Number of Initiatives'},
            height=500
        )
        state_chart.update_layout(
            legend_title_text='Renewable Source',
            barmode='stack',
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        time_chart = px.line(
            filtered_data.groupby(['Fiscal Year', 'Source']).size().reset_index(name='Count'),
            x='Fiscal Year',
            y='Count',
            color='Source',
            color_discrete_sequence=color_palette[:len(selected_sources)],
            markers=True,
            title=f'Renewable Energy Over Time ({years_range[0]}-{years_range[1]})',
            labels={'Count': 'Number of Initiatives', 'Fiscal Year': 'Year'},
            height=500
        )
        time_chart.update_layout(
            legend_title_text='Renewable Source',
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        time_chart.update_traces(line=dict(width=3))
        
        return state_chart, time_chart
    
    return app, server

if __name__ == '__main__':
    mitigations_cleaned = pd.read_csv('mitigations_cleaned.csv')
    extended_palette = ["#DF7350", "#173647", "#007786","#3F5D6C","#C3BCB7", "#9ABBD9", "#F2B880", "#8B5E88", "#D1B963", "#E58B88"]

    app, server = create_renewable_dashboard(mitigations_cleaned, extended_palette)
    app.run(debug=False, host='0.0.0.0', port=8080)
