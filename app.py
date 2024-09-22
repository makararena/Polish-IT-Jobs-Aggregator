from dash import Dash, html, dcc, Input, Output
from matplotlib import colors as mcolors
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import datetime
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import pandas as pd
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv
load_dotenv()

from data.constants_and_mappings import PLOT_COLUMNS, LANGUAGES, PROJECT_DESCRIPTION
from database_interface import fetch_data, create_engine_from_config
from data.database_queries import ALL_JOBS_QUERY

geojson_path = './data/poland.voivodeships.json'
with open(geojson_path, 'r') as file:
    poland_geojson = json.load(file)

engine = create_engine_from_config()

df = fetch_data(ALL_JOBS_QUERY, engine)
print(df.head())
df.columns = PLOT_COLUMNS

df['StartSalary'] = pd.to_numeric(df['StartSalary'], errors='coerce')
df['MaxSalary'] = pd.to_numeric(df['MaxSalary'], errors='coerce')

df['StartSalary'] = df['StartSalary'].fillna(0)
df['MaxSalary'] = df['MaxSalary'].fillna(0)

df['DatePosted'] = pd.to_datetime(df['DatePosted'])
df['Expiration'] = pd.to_datetime(df['Expiration'])

df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.').str.split(';').str[0]
df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.').str.split(';').str[0]

df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

df['Latitude'] = df['Latitude'].fillna(0)
df['Longitude'] = df['Longitude'].fillna(0)

last_update_date = max(df['DatePosted'])

# last_update_date = 
app = Dash(__name__)

custom_colorscale = [
    [0, 'rgb(239, 237, 245)'],  
    [0.5, 'rgb(188, 189, 220)'],  
    [1, 'rgb(117, 107, 177)']     
]

app.layout = html.Div(children=[
    html.H1(
        children='🇵🇱 IT Jobs Aggregator 🇵🇱',
        style={'font-family': 'Arial', 'font-size': '40px', 'text-align': 'center', 'color': '#333'}
    ),
    html.Div(
        children=[
            dcc.Markdown(
                children=PROJECT_DESCRIPTION,
                style={'font-family': 'Arial', 'font-size': '18px', 'text-align': 'left', 'color': '#333', 'width': '60%', 'margin-left': 'auto', 'font-weight': '700','padding': '20px'}
            ),
            html.Img(
                src='/assets/ProjectSchemaWH.png',
                style={'width': '900px', 'height': 'auto', 'margin-left': 'auto'}
            )
        ],
        style={'display': 'flex', 'align-items': 'center', 'justify-content': 'flex-end', 'margin-bottom': '20px','margin-right': '40px'}
    ),
    html.Div([
        html.Div([
            html.H4(id='yesterday-jobs', style={
                'font-family': 'Arial', 
                'font-size': '20px', 
                'color': '#333',
                'text-align': 'center',
                'padding': '10px',
                'line-height': '1.6',
                'text-decoration': 'underline'
            }),
            html.H4(id='current-jobs', style={
                'font-family': 'Arial', 
                'font-size': '20px', 
                'color': '#333',
                'text-align': 'center',
                'padding': '10px',
                'line-height': '1.6',
                'text-decoration': 'underline'
            }),
            html.H4(id='total-jobs', style={
                'font-family': 'Arial', 
                'font-size': '20px', 
                'color': '#333',
                'text-align': 'center',
                'padding': '10px',
                'line-height': '1.6',
                'text-decoration': 'underline'
            })
        ], style={
            'display': 'flex',
            'justify-content': 'space-around',  
            'align-items': 'center',        
            'width': '80%',               
            'margin': '0 auto'          
        }),

    ], style={'margin-bottom': '30px'}),  
    html.P(
        children=f"Data is updated as of {last_update_date}.",
        style={'font-family': 'Arial', 'font-size': '15px', 'text-align': 'center', 'margin-bottom': '20px', 'color': 'grey'}
    ),
    html.Div([
        html.Button("Download Filtered Data", id="download-button", n_clicks=0),
        dcc.Download(id="download-data")
    ], style={'text-align': 'center', 'margin-top': '20px'}),
    
    html.Div(style={
        'height': '2px',
        'backgroundColor': '#ccc',
        'width': '100%',
        'margin': '20px 0'
    }),
    
    html.H4(
        children="Filters",
        style={'font-family': 'Arial', 'font-size': '24px', 'text-align': 'center', 'margin-bottom': '20px','color': '#333'}
    ),
    
    html.Div(
        children=[
        html.Div(
            children=[
                html.Label(
                    'Experience Level:',
                    style={
                        'font-family': 'Arial',
                        'font-size': '16px',
                        'font-weight': 'bold',
                        'color': '#333',
                        'margin-bottom': '10px'
                    }
                ),
                dcc.Checklist(
                    id='experience',
                    options=[{'label': exp, 'value': exp} for exp in ['Internship', 'Junior', 'Middle', 'Senior', 'Lead']],
                    inline=True,
                    style={
                        'font-family': 'Arial',
                        'font-size': '14px',
                        'padding': '10px',
                        'margin-top': '5px'  
                    },
                    inputStyle={"margin-right": "10px"}
                )
            ],
            style={
                'display': 'flex',
                'flex-direction': 'column',
                'align-items': 'flex-start',
                'margin-right': '20px',
                'min-width': '250px',
                'overflow': 'auto',
                'padding': '15px'
            }
        ),
            html.Div(
                children=[
                    html.Label(
                        'Sphere of Work:',
                        style={'font-family': 'Arial', 'font-size': '16px', 'font-weight': 'bold', 'color': '#333'}
                    ),
                    dcc.Checklist(
                        id='job',
                        options=[{'label': role, 'value': role} for role in df['CoreRole'].value_counts().head(30).index],
                        inline=True,
                        style={'font-family': 'Arial', 'font-size': '14px', 'padding': '10px'},
                        inputStyle={"margin-right": "10px"}
                    )
                ],
                style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start', 'margin-right': '20px'}
            ),
            html.Div(
                children=[
                    html.Label(
                        'Jobs Date Range:',
                        style={'font-family': 'Arial', 'font-size': '16px', 'font-weight': 'bold', 'color': '#333'}
                    ),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['DatePosted'].min().date(),
                        end_date=df['DatePosted'].max().date(),
                        display_format='YYYY-MM-DD',
                        style={'font-family': 'Arial', 'font-size': '14px', 'padding': '10px'}
                    )
                ],
                style={
                'display': 'flex',
                'flex-direction': 'column',
                'align-items': 'flex-start',
                'margin-right': '20px',
                'min-width': '250px',
                'overflow': 'auto',
                'padding': '15px'
            }
            )
        ],
        style={
            'display': 'flex',
            'justify-content': 'center',
            'align-items': 'center',
            'gap': '20px',
            'margin-bottom': '20px'
        }
    ),
    
    html.Div(style={
        'height': '2px',
        'backgroundColor': '#ccc',
        'width': '100%',
        'margin': '20px 0'
    }),
    
    html.H4(
        children="Time-Series Analysis of Job Offers",
        style={'font-family': 'Arial', 'font-size': '24px', 'text-align': 'center', 'margin-bottom': '20px','color': '#333'}
    
    ),
    
    html.Div([
        html.Div(children=[
            html.Div(dcc.Graph(id='line-chart-day'), style={'width': '50%', 'margin-top': '20px'}),
            html.Div(dcc.Graph(id='bar-chart-month'), style={'width': '50%', 'margin-top': '20px'})
        ], style={'display': 'flex', 'justify-content': 'center'}),
        
        html.Div(style={
            'height': '2px',
            'backgroundColor': '#ccc',
            'width': '100%',
            'margin': '20px 0'
        }),
        
        html.H4(
            children="Location of Job Offers in Poland",
            style={'font-family': 'Arial', 'font-size': '24px', 'text-align': 'center', 'margin-bottom': '20px','color': '#333'}
        ),
        
        html.Div(children=[
            html.Div(dcc.Graph(id='map'), style={'width': '50%', 'margin-top': '20px'}),
            html.Div(dcc.Graph(id='map-cities'), style={'width': '60%', 'margin-top': '20px'})
        ], style={'display': 'flex', 'justify-content': 'center'}),

        html.Div(children=[
            html.Div(dcc.Graph(id='pie'), style={'width': '50%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(id='pie_cities'), style={'width': '50%', 'display': 'inline-block'}),
        ], style={'display': 'flex', 'justify-content': 'center'}),
        
        html.Div(style={
            'height': '2px',
            'backgroundColor': '#ccc',
            'width': '100%',
            'margin': '20px 0'
        }),
        html.H4(
        children="Spheres, Technologies, Benefits and Languages",
        style={'font-family': 'Arial', 'font-size': '24px', 'text-align': 'center', 'margin-bottom': '20px','color': '#333'}
    
    ),
        
        html.Div(dcc.Graph(id='bar_tachnologies'), style={'width': '100%', 'margin-top': '20px'}),
        
        html.Div(children=[
            html.Div(dcc.Graph(id='pie_benefits'), style={'width': '50%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(id='language-bar'), style={'width': '50%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justify-content': 'center'}),
        
        html.Div(style={
            'height': '2px',
            'backgroundColor': '#ccc',
            'width': '100%',
            'margin': '20px 0'
        }),
        html.H4(
        children="Roles, Experience Levels, Salary and Employers", 
        style={'font-family': 'Arial', 'font-size': '24px', 'text-align': 'center', 'margin-bottom': '20px','color': '#333'}
    
    ),
        html.Div(dcc.Graph(id='roles_bar'), style={'width': '100%', 'margin-top': '20px'}),
        html.Div(children=[
            html.Div(dcc.Graph(id='experience-bar'), style={'width': '50%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(id='pie_work_schedule'), style={'width': '50%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justify-content': 'center'}),
        html.Div(dcc.Graph(id='salary-boxplot'), style={'width': '100%', 'margin-top': '20px'}),
        html.Div(dcc.Graph(id='employers_bar'), style={'width': '100%', 'margin-top': '20px'}),

html.Div([
    html.Div("Find me on:", style={'font-family': 'Arial', 'font-size': '16px', 'text-align': 'center', 'margin-bottom': '10px', 'color': '#333', 'margin-top': '10px'}),
    html.Div([
        html.A("GitHub", href="https://github.com/makararena", target="_blank", style={'font-family': 'Arial', 'font-size': '16px', 'color': '#333', 'margin-right': '10px'}),
        html.A("LinkedIn", href="https://www.linkedin.com/in/makar-charviakou-b72526279/", target="_blank", style={'font-family': 'Arial', 'font-size': '16px', 'color': '#333', 'margin-right': '10px'}),
        html.A("Email", href="makararena@gmail.com", target="_blank", style={'font-family': 'Arial', 'font-size': '16px', 'color': '#333'})
    ], style={'text-align': 'center', 'padding': '10px'})
], style={'text-align': 'center', 'margin-top': '40px', 'border-top': '1px solid #ccc'})
        
    ])
])

@app.callback(
    [Output('yesterday-jobs', 'children'),
     Output('current-jobs', 'children'),
     Output('total-jobs', 'children'),
     Output('line-chart-day', 'figure'),
     Output('bar-chart-month', 'figure'),
     Output('map', 'figure'),
     Output('map-cities', 'figure'),
     Output('pie', 'figure'),
     Output('pie_cities', 'figure'),
     Output('experience-bar', 'figure'),
     Output('language-bar', 'figure'),
     Output('salary-boxplot', 'figure'),
     Output('pie_benefits', 'figure'),
     Output('pie_work_schedule', 'figure'),
     Output('bar_tachnologies', 'figure'),
     Output('employers_bar', 'figure'),
     Output('roles_bar', 'figure')],
    [Input('experience', 'value'),
     Input('job', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_figures(selected_experiences, selected_jobs, start_date, end_date):
    start_date = pd.to_datetime(start_date, errors='coerce')
    end_date = pd.to_datetime(end_date, errors='coerce')

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    df_filtered = df[(df['DatePosted'] >= start_date) & (df['DatePosted'] <= end_date)]

    if selected_experiences:
        valid_experiences = [exp for exp in selected_experiences if exp in df.columns]
        if valid_experiences:
            df_filtered = df_filtered[df_filtered[valid_experiences].sum(axis=1) > 0]

    if selected_jobs:
        df_filtered = df_filtered[df_filtered['CoreRole'].isin(selected_jobs)]

    # ----------
    # Day Histogram Chart
    # ----------     
        
    df_filtered['day'] = df_filtered['DatePosted'].dt.date
    daily_counts = df_filtered['day'].value_counts().reset_index()
    daily_counts.columns = ['Day', 'Count']
    daily_counts = daily_counts.sort_values(by='Day')
    daily_counts['Day'] = pd.to_datetime(daily_counts['Day'])
    
    figure_line_day = px.line(daily_counts, x='Day', y='Count',
                            title='Number of Job Offers per Day',
                            labels={'Day': 'Day', 'Count': 'Number of Offers'},
                            markers=True)
    figure_line_day.update_layout(xaxis_title='Day', yaxis_title='Number of Offers')


    # ----------
    # Month Histogram Chart
    # ----------  

    df_filtered['month'] = df_filtered['DatePosted'].dt.to_period('M').astype(str)
    monthly_counts = df_filtered['month'].value_counts().reset_index()
    monthly_counts.columns = ['Month', 'Count']
    monthly_counts = monthly_counts.sort_values(by='Month')
    monthly_counts['Month'] = pd.to_datetime(monthly_counts['Month'], format='%Y-%m')

    # Create a bar chart instead of a line chart
    figure_bar_month = px.bar(monthly_counts, x='Month', y='Count',
                            title='Number of Job Offers per Month',
                            labels={'Month': 'Month', 'Count': 'Number of Offers'})

    # Update the layout for better visualization
    figure_bar_month.update_layout(xaxis_title='Month', yaxis_title='Number of Offers',
                                xaxis=dict(tickformat='%Y-%m', tickangle=-45))
  
    
    # ----------
    # Poland Map Chart
    # ----------    
    
    df_filtered['Region'] = df_filtered['Region'].str.upper()
    df_filtered = df_filtered.assign(Region=df_filtered['Region'].str.split(';')).explode('Region')
    df_grouped_filtered = df_filtered.groupby('Region').size().reset_index(name='count')
    df_grouped_filtered = df_grouped_filtered.rename(columns={'Region': 'name'})
    df_grouped_filtered = df_grouped_filtered.sort_values(by='count', ascending=False)

    data_for_map_filtered = pd.merge(pd.DataFrame({'name': poland_geojson}), df_grouped_filtered, on='name', how='left').fillna(0)
    data_for_map_filtered = data_for_map_filtered.sort_values(by='count', ascending=False)

    figure_polska_filtered = go.Figure(go.Choroplethmapbox(
        geojson=poland_geojson,
        locations=data_for_map_filtered['name'],
        featureidkey="properties.name",
        z=data_for_map_filtered['count'],
        colorscale=custom_colorscale, 
        showscale=True,
        ))

    figure_polska_filtered.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=51.9194, lon=19.1451),
            zoom=4
        ),
        title_text="Number Of Jobs Per Region",
    )
    
    figure_histogram_filtered = px.histogram(df_filtered, x='Region', title='Job Counts per Region', labels={'Region': 'Region'})
    figure_histogram_filtered.update_layout(xaxis_title='Region', yaxis_title='Count')
    figure_histogram_filtered.update_xaxes(categoryorder='total descending')

    figure_bar_filtered = px.bar(df_grouped_filtered, x='name', y='count', title='Job Counts by Region', labels={'name': 'Region', 'count': 'Count'})
    figure_bar_filtered.update_layout(xaxis_title='Region', yaxis_title='Count')
    figure_bar_filtered.update_xaxes(categoryorder='total descending')

    df_top_10 = df_grouped_filtered.head(10)

    fig_pie_filtered = px.pie(
        df_top_10, 
        names='name', 
        values='count', 
        title='Distribution of Job Offers by Region', 
        labels={'name': 'Region', 'count': 'Job Offers'}, 
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_pie_filtered.update_traces(textinfo='percent+label')
    
    # ----------
    # Poland Cities Chart
    # ----------    

    # Process city data
    df_filtered['City'] = df_filtered['City'].replace('Warsaw', 'Warszawa')
    df_filtered['City'] = df_filtered['City'].astype(str)
    df_filtered['Latitude'] = df_filtered['Latitude'].astype(str)
    df_filtered['Longitude'] = df_filtered['Longitude'].astype(str)

    df_filtered['City'] = df_filtered['City'].apply(lambda x: x.split(';'))
    df_filtered['Latitude'] = df_filtered['Latitude'].apply(lambda x: x.split(';'))
    df_filtered['Longitude'] = df_filtered['Longitude'].apply(lambda x: x.split(';'))

    df_filtered = df_filtered[df_filtered['City'].str.len() == df_filtered['Latitude'].str.len()]
    df_filtered = df_filtered[df_filtered['City'].str.len() == df_filtered['Longitude'].str.len()]

    df_filtered = df_filtered.explode(['City', 'Latitude', 'Longitude'])

    city_counts = df_filtered['City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Count']

    df_cities = df_filtered[['City', 'Latitude', 'Longitude']].drop_duplicates()

    city_data = pd.merge(city_counts, df_cities, on='City', how='left')

    city_data = city_data.dropna(subset=['Latitude', 'Longitude'])

    max_size = 40
    min_size = 10
    size_range = city_data['Count'].max() - city_data['Count'].min()

    if size_range > 0:
        city_data['Size'] = min_size + (max_size - min_size) * (city_data['Count'] - city_data['Count'].min()) / size_range
    else:
        city_data['Size'] = min_size
    
    fig_city_bubbles = go.Figure(go.Scattergeo(
        lat=city_data['Latitude'],
        lon=city_data['Longitude'],
        mode='markers',
        marker=dict(
            size=city_data['Size'],
            opacity=0.6,                ),
        text=city_data[['City','Count']],
        textposition='top center',
        geojson = poland_geojson
    ))

    fig_city_bubbles.update_layout(
        geo=dict(
            landcolor='rgb(242, 242, 242)',
            subunitcolor='rgb(100, 217, 217)',
            countrycolor='rgb(0, 0, 0)',
            center=dict(lat=51.9194, lon=19.1451),  # Center of Poland
            projection_scale=19, 
            showcountries=True,
            showland=True,
        ),
        title_text="City Job Offer Distribution in Poland",
    )

    # ----------
    # City Distribution Pie Chart
    # ----------
    
    City_counts = df_filtered['City'].value_counts().reset_index()
    City_counts.columns = ['City', 'Count']
    top_cities = City_counts.head(9)
    others_count = City_counts.iloc[9:]['Count'].sum()
    others_df = pd.DataFrame({'City': ['Others'], 'Count': [others_count]})
    top_cities = pd.concat([top_cities, others_df], ignore_index=True)
    fig_pie_cities = px.pie(top_cities, names='City', values='Count', title='City Distribution of Job Offers', labels={'City': 'City', 'Count': 'Count'}, color_discrete_sequence=px.colors.sequential.Viridis)

    # ----------
    # Languages Bar Chart
    # ----------
    df_languages_filtered = df_filtered[LANGUAGES.keys()].sum().reset_index()
    df_languages_filtered.columns = ['Language', 'Count']
    figure_languages_bar_filtered = px.bar(df_languages_filtered, x='Language', y='Count', 
                                          title='Languages Distribution', 
                                          labels={'Language': 'Language', 'Count': 'Count'})
    figure_languages_bar_filtered.update_layout(xaxis_title='', yaxis_title='')
    figure_languages_bar_filtered.update_xaxes(categoryorder='total descending')

    # ----------
    # Benefits Pie Chart
    # ----------
    df_benefits_filtered = df_filtered[['WorkLifeBalance','FinancialRewards','HealthWellbeing',
                                        'Development','WorkplaceCulture','MobilityTransport',
                                        'UniqueBenefits','SocialInitiatives']].sum().reset_index()
    df_benefits_filtered.columns = ['Benefit', 'Count']
    figure_benefits_pie = px.pie(df_benefits_filtered, names='Benefit', values='Count', 
                                title='Benefits Distribution',
                                labels={'Benefit': 'Benefit', 'Count': 'Count'},
                                color_discrete_sequence=px.colors.sequential.Viridis)
    figure_benefits_pie.update_layout(
        legend_title_text='Benefit',
        title={'text': 'Benefits Distribution', 'x':0.5},
        margin=dict(t=50, b=50, l=50, r=50)
    )
    # ----------
    # Employment Type Pie Chart
    # ----------

    df_employment_type_filtered = df_filtered[['FullTime', 'Hybrid', 'Remote']].sum().reset_index()
    df_employment_type_filtered.columns = ['Employment Type', 'Count'] 

    figure_employment_type_pie = px.pie(df_employment_type_filtered, names='Employment Type', values='Count', 
                                        title='Employment Type Distribution',
                                        labels={'Employment Type': 'Employment Type', 'Count': 'Count'},
                                        color_discrete_sequence=px.colors.sequential.Viridis)

    figure_employment_type_pie.update_layout(
        legend_title_text='Employment Type',
        title={'text': 'Employment Type Distribution', 'x': 0.5},
        margin=dict(t=50, b=50, l=50, r=50)
    )

    # ----------
    # Experience Level Bar Chart
    # ----------
    df_experiences_filtered = df_filtered[['Internship','Junior','Middle','Senior','Lead']].sum().reset_index()
    
    df_experiences_filtered.columns = ['Experience', 'Count']

    figure_experiences_bar_filtered = px.bar(df_experiences_filtered, x='Experience', y='Count', 
                                            title='Experience Level Distribution', 
                                            labels={'Experience': 'Experience', 'Count': 'Count'})
    figure_experiences_bar_filtered.update_layout(xaxis_title='', yaxis_title='')

    # ----------
    # Salary Box Plot
    # ----------

    color_map = {
        'Internship': 'blue',
        'Junior': 'orange',
        'Middle': 'red',
        'Senior': 'purple',
        'Lead': 'green'
    }

    def lighten_color(color, factor=0.3):
        """Lighten the given color by the given factor."""
        rgb = mcolors.hex2color(color)
        rgb = [min(1, x + factor) for x in rgb]
        return mcolors.rgb2hex(rgb)

    figure_salary_boxplot = go.Figure()

    experience_levels = ['Internship', 'Junior', 'Middle', 'Senior', 'Lead']
    colors = [color_map[exp] for exp in experience_levels]
    
    for exp, color in zip(experience_levels, colors):
        df_exp = df_filtered[df_filtered[exp] == 1]
        df_exp = df_exp[df_exp['StartSalary'] != 0]

        Q1 = df_exp['StartSalary'].quantile(0.25)
        Q3 = df_exp['StartSalary'].quantile(0.75)
        IQR = Q3 - Q1

        upper_bound = Q3 + 10 * IQR

        df_exp = df_exp[df_exp['StartSalary'] <= upper_bound]
                
        figure_salary_boxplot.add_trace(go.Box(
            y=df_exp['StartSalary'],
            name=f'Start Salary ({exp})',
            marker_color=color,
            boxmean='sd' 
        ))
        
        figure_salary_boxplot.add_trace(go.Box(
            y=df_exp['MaxSalary'],
            name=f'Max Salary ({exp})',
            marker_color=lighten_color(color),
            boxmean='sd'
        ))

    figure_salary_boxplot.update_layout(
        title='Salary Distribution by Experience Level',
        xaxis_title='Experience Level',
        yaxis_title='Salary',
        boxmode='group'
    )
    
    # ----------
    # Technologies Bar Chart
    # ----------
    
    all_technologies = df_filtered['Technologies'].str.split('[,;]', expand=True).stack()
    all_technologies = all_technologies.astype(str).str.strip().str.upper()

    tech_counts = all_technologies.value_counts().reset_index()
    tech_counts.columns = ['Technology', 'Count']

    tech_counts = tech_counts[tech_counts['Technology'] != '']

    top_technologies = tech_counts.nlargest(50, 'Count')

    figure_technologies_bar = px.bar(top_technologies, 
                                    x='Technology', 
                                    y='Count', 
                                    title='Top 50 Most Popular Technologies', 
                                    labels={'Technology': 'Technology', 'Count': 'Count'})

    figure_technologies_bar.update_layout(
        xaxis_title='', 
        yaxis_title='',
        xaxis_tickangle=-45
    )
    figure_technologies_bar.update_xaxes(categoryorder='total descending')
    
    # ----------
    # Employer Bar Chart
    # ----------
    employer_counts = df_filtered['Employer'].value_counts().reset_index()
    employer_counts.columns = ['Employer', 'Count']
    top_employers = employer_counts.nlargest(20, 'Count')

    figure_employers_bar = px.bar(top_employers, 
                                x='Employer', 
                                y='Count', 
                                title='Top 20 Employers by Number of Job Listings', 
                                labels={'Employer': 'Employer', 'Count': 'Count'})
    figure_employers_bar.update_layout(
        xaxis_title='', 
        yaxis_title='',
        xaxis_tickangle=-45
    )
    figure_employers_bar.update_xaxes(categoryorder='total descending')
    
    # ----------
    # Positions Bar Chart
    # ----------
    role_counts = df['CoreRole'].value_counts().reset_index()
    role_counts.columns = ['Role', 'Count']
    
    top_roles = role_counts.head(30)
    
    figure_roles_bar = px.bar(top_roles,
                         x='Role',
                         y='Count',
                         title='Top 30 Roles by Number of Listings',
                         labels={'Role': 'Role', 'Count': 'Count'})
    
    figure_roles_bar.update_layout(
    xaxis_title='', 
    yaxis_title='', 
    xaxis_tickangle=-45
)
    figure_roles_bar.update_xaxes(categoryorder='total descending')
    
    yesterday_date = (datetime.today() - timedelta(days=1)).date()
    today_date = datetime.today().date()

    # Calculate counts
    yesterday_jobs_count = str(df[df['DatePosted'].dt.date == yesterday_date].shape[0]) + " Jobs Were Posted Yesterday"
    active_jobs_count = str(df[df['Expiration'].dt.date > today_date].shape[0]) + " Jobs Are Active Now"
    total_jobs_count = str(df.shape[0]) + " Jobs Are In This Database"

    return yesterday_jobs_count, active_jobs_count, total_jobs_count, figure_line_day, figure_bar_month, figure_polska_filtered, fig_city_bubbles, fig_pie_filtered, fig_pie_cities, \
            figure_experiences_bar_filtered, figure_languages_bar_filtered, figure_salary_boxplot, figure_benefits_pie, \
            figure_employment_type_pie, figure_technologies_bar, figure_employers_bar, figure_roles_bar

@app.callback(
    Output("download-data", "data"),
    Output("download-button", "n_clicks"),
    Input("download-button", "n_clicks"),
    [Input('experience', 'value'),
     Input('job', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def download_filtered_data(n_clicks, selected_experiences, selected_jobs, start_date, end_date):
    if n_clicks == 0:
        raise PreventUpdate

    start_date = pd.to_datetime(start_date, errors='coerce')
    end_date = pd.to_datetime(end_date, errors='coerce')

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    df_filtered = df[(df['DatePosted'] >= start_date) & (df['DatePosted'] <= end_date)]

    if selected_experiences:
        valid_experiences = [exp for exp in selected_experiences if exp in df.columns]
        if valid_experiences:
            df_filtered = df_filtered[df_filtered[valid_experiences].sum(axis=1) > 0]

    if selected_jobs:
        df_filtered = df_filtered[df_filtered['CoreRole'].isin(selected_jobs)]
    else:
        top_roles = df['CoreRole'].value_counts().head(20).index
        df_filtered = df_filtered[df_filtered['CoreRole'].isin(top_roles)]

    csv_string = df_filtered.to_csv(index=False, encoding='utf-8')

    return dict(content=csv_string, filename="filtered_data.csv"), 0

if __name__ == '__main__':
    app.run_server(debug=False)