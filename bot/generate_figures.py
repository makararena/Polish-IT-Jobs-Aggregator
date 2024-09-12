import json
import os
import shutil
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import date, datetime, timedelta
import sys
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import colors as mcolors
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.dictionaries import languages, plot_columns, not_valid_technologies, keep_technologies

import warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

db_config = {
    "host": "localhost",
    "database": "polish_it_jobs_aggregator",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD")
}

def connect_db(db_config):
    """Establish a database connection and return the connection object."""
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def fetch_data(query, db_config):
    """Establish a database connection and retrieve data."""
    try:
        with psycopg2.connect(**db_config) as conn:
            return pd.read_sql_query(query, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return pd.DataFrame()

query = "SELECT * FROM jobs;"
query_yesterday = "SELECT * FROM jobs WHERE date_posted = CURRENT_DATE - INTERVAL '1 day';"

def generate_figures(df,chat_id, histogram_day_month_chart=True, map_chart=True, cities_chart=True, city_pie_chart=True, 
                     languages_bar_chart=True, benefits_pie_chart=True, employment_type_pie_chart=True, 
                     experience_level_bar_chart=True, salary_box_plot=True, technologies_bar_chart=True, 
                     employer_bar_chart=True, positions_bar_chart=True, post_text=True, content_daily=True, light_theme=True) :
    df_plot = df.copy()
    df_plot = df_plot[df_plot['date_posted'] != date(2024, 9, 2)]
    df_plot.columns = plot_columns
    
    df_plot['StartSalary'] = pd.to_numeric(df_plot['StartSalary'], errors='coerce')
    df_plot['MaxSalary'] = pd.to_numeric(df_plot['MaxSalary'], errors='coerce')

    df_plot['StartSalary'] = df_plot['StartSalary'].fillna(0)
    df_plot['MaxSalary'] = df_plot['MaxSalary'].fillna(0)
    
    df_plot['Salary'] = (df_plot['StartSalary'] + df_plot['MaxSalary']) / 2
    df_plot['Salary'] = df_plot['Salary'].fillna(0)

    df_plot['DatePosted'] = pd.to_datetime(df_plot['DatePosted'])
    df_plot['Expiration'] = pd.to_datetime(df_plot['Expiration'])

    df_plot['Latitude'] = df_plot['Latitude'].astype(str).str.replace(',', '.').str.split(';').str[0]
    df_plot['Longitude'] = df_plot['Longitude'].astype(str).str.replace(',', '.').str.split(';').str[0]

    df_plot['Latitude'] = pd.to_numeric(df_plot['Latitude'], errors='coerce')
    df_plot['Longitude'] = pd.to_numeric(df_plot['Longitude'], errors='coerce')

    df_plot['Latitude'] = df_plot['Latitude'].fillna(0)
    df_plot['Longitude'] = df_plot['Longitude'].fillna(0)
    
    geojson_path = '../data/poland.voivodeships.json'
    with open(geojson_path, 'r') as file:
        poland_geojson = json.load(file)

    geojson_names = [feature['properties']['name'] for feature in poland_geojson['features']]

    custom_colorscale_white = [
        [0, 'rgb(239, 237, 245)'],  
        [0.5, 'rgb(188, 189, 220)'],  
        [1, 'rgb(117, 107, 177)']     
    ]
    custom_colorscale_dark = [
        [0, 'rgb(26, 26, 51)'],
        [0.5, 'rgb(51, 51, 102)'],
        [1, 'rgb(102, 102, 153)'] 
    ]
    
    
    custom_colorscale = custom_colorscale_dark
    landcolor='rgb(10, 10, 10)'
    oceancolor='rgb(0, 0, 50)'
    lakecolor='rgb(0, 0, 70)'
    countrycolor='rgb(255, 255, 255)'
    coastlinecolor='rgb(255, 255, 255)'
    template="plotly_dark"
    style = "carto-darkmatter"
    border_color="rgb(255, 255, 255)"
    if light_theme:
        custom_colorscale = custom_colorscale_white
        template="plotly"
        style = "carto-positron"
        landcolor='rgb(242, 242, 242)'
        oceancolor='rgb(217, 234, 247)'
        lakecolor='rgb(200, 225, 255)'
        countrycolor='rgb(200, 200, 200)'
        coastlinecolor='rgb(150, 150, 150)'
        
        
    folder_path = f"figures/{chat_id}"
    os.makedirs(folder_path, exist_ok=True)
    
    if histogram_day_month_chart:
        # Day Histogram Chart
        df_plot['day'] = df_plot['DatePosted'].dt.date
        daily_counts = df_plot['day'].value_counts().reset_index()
        daily_counts.columns = ['Day', 'Count']
        daily_counts = daily_counts.sort_values(by='Day')
        daily_counts['Day'] = pd.to_datetime(daily_counts['Day'])
        if daily_counts.empty:
            print("No data available to plot.")
        else:
            figure_line_day = px.line(
                daily_counts, 
                x='Day', 
                y='Count',
                title='Number of Job Offers per Day',
                labels={'Day': 'Day', 'Count': 'Number of Offers'},
                markers=True,
                template=template
            )
            
            figure_line_day.update_layout(
                title=dict(text='Number of Job Offers per Day', font=dict(size=40)),
                xaxis_title=dict(text='Day', font=dict(size=25)),
                yaxis_title=dict(text='Number of Offers', font=dict(size=25)),
                xaxis=dict(tickfont=dict(size=22)),
                yaxis=dict(tickfont=dict(size=22))
            )
            
            figure_line_day.write_image(f'{folder_path}/day_histogram.png', width=1920, height=1080)

        df_plot['month'] = df_plot['DatePosted'].dt.to_period('M').astype(str)
        monthly_counts = df_plot['month'].value_counts().reset_index()
        monthly_counts.columns = ['Month', 'Count']
        monthly_counts = monthly_counts.sort_values(by='Month')
        monthly_counts['Month'] = pd.to_datetime(monthly_counts['Month'], format='%Y-%m')

        if len(monthly_counts['Month'].unique()) > 1:
            figure_bar_month = px.bar(monthly_counts, x='Month', y='Count',
                                    title='Number of Job Offers per Month',
                                    labels={'Month': 'Month', 'Count': 'Number of Offers'})
            
            figure_bar_month.update_layout(
                xaxis_title='Month', yaxis_title='Number of Offers',
                xaxis=dict(tickformat='%Y-%m', tickangle=-45),
                template=template
            )
            figure_bar_month.write_image(f'{folder_path}/month_histogram.png', width=1920, height=1080)

        df_plot['weekday'] = df_plot['DatePosted'].dt.day_name()
        weekday_counts = df_plot['weekday'].value_counts().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]).reset_index()
        weekday_counts.columns = ['Weekday', 'Count']
        weekday_counts = weekday_counts.sort_values(by='Weekday', key=lambda x: pd.Categorical(x, categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ordered=True))

        if weekday_counts.empty:
            print("No data available to plot for weekdays.")
        else:
            figure_bar_weekday = px.bar(
                weekday_counts, 
                x='Weekday', 
                y='Count',
                title='Number of Job Offers per Weekday',
                labels={'Weekday': 'Weekday', 'Count': 'Number of Offers'}
            )
            
            figure_bar_weekday.update_layout(
                xaxis_title='Weekday', 
                yaxis_title='Number of Offers',
                xaxis=dict(
                    tickangle=-45,
                    tickfont=dict(size=20)
                ),
                yaxis=dict(
                    tickfont=dict(size=20)
                ),
                template=template
            )
            figure_bar_weekday.write_image(f'{folder_path}/weekday_histogram.png', width=1920, height=1080)
    
    if map_chart:
        df_plot['Region'] = df_plot['Region'].str.upper()
        df_plot = df_plot.assign(Region=df_plot['Region'].str.split(';')).explode('Region')
        df_grouped = df_plot.groupby('Region').size().reset_index(name='count')
        df_grouped = df_grouped.rename(columns={'Region': 'name'})
        df_grouped = df_grouped.sort_values(by='count', ascending=False)
        
        data_for_map = pd.merge(pd.DataFrame({'name': geojson_names}), df_grouped, on='name', how='left').fillna(0)
        data_for_map = data_for_map.sort_values(by='count', ascending=False)
        if data_for_map['count'].sum() > 0:
            figure_polska = go.Figure(go.Choroplethmapbox(
                geojson=poland_geojson,
                locations=data_for_map['name'],
                featureidkey="properties.name", 
                z=data_for_map['count'],
                colorscale=custom_colorscale,
                showscale=True,
            ))
            
            figure_polska.update_layout(
                mapbox=dict(
                    style=style,
                    center=dict(lat=51.9194, lon=19.1451),
                    zoom=6
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                template=template, 
            )
            figure_polska.write_image(f'{folder_path}/poland_map.png', width=1920, height=1080)

    if cities_chart: 
        df_filtered_cities_map = df_plot.copy()
        df_filtered_cities_map['City'] = df_filtered_cities_map['City'].replace('Warsaw', 'Warszawa')
        df_filtered_cities_map['City'] = df_filtered_cities_map['City'].astype(str)
        df_filtered_cities_map['Latitude'] = df_filtered_cities_map['Latitude'].astype(str)
        df_filtered_cities_map['Longitude'] = df_filtered_cities_map['Longitude'].astype(str)
        df_filtered_cities_map['City'] = df_filtered_cities_map['City'].apply(lambda x: x.split(';'))
        df_filtered_cities_map['Latitude'] = df_filtered_cities_map['Latitude'].apply(lambda x: x.split(';'))
        df_filtered_cities_map['Longitude'] = df_filtered_cities_map['Longitude'].apply(lambda x: x.split(';'))
        
        df_filtered_cities_map = df_filtered_cities_map[df_filtered_cities_map['City'].str.len() == df_filtered_cities_map['Latitude'].str.len()]
        df_filtered_cities_map = df_filtered_cities_map[df_filtered_cities_map['City'].str.len() == df_filtered_cities_map['Longitude'].str.len()]

        df_filtered_cities_map = df_filtered_cities_map.explode(['City', 'Latitude', 'Longitude'])

        city_counts = df_filtered_cities_map['City'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']

        df_cities = df_filtered_cities_map[['City', 'Latitude', 'Longitude']].drop_duplicates()

        city_data = pd.merge(city_counts, df_cities, on='City', how='left')

        city_data = city_data.dropna(subset=['Latitude', 'Longitude'])

        max_size = 50
        min_size = 20
        size_range = city_data['Count'].max() - city_data['Count'].min()

        if size_range > 0:
            city_data['Size'] = min_size + (max_size - min_size) * (city_data['Count'] - city_data['Count'].min()) / size_range
        else:
            city_data['Size'] = min_size
        
        remote_coordinates = (city_data['Latitude'] == 0.0) & (city_data['Longitude'] == 0.0)
        if (not city_data.empty) and (not remote_coordinates.all()):
            fig_city_bubbles = go.Figure()

            fig_city_bubbles.add_trace(
                go.Scattermapbox(
                    mode='markers',
                    lat=city_data['Latitude'],
                    lon=city_data['Longitude'],
                    marker=dict(
                        size=city_data['Size'],
                        opacity=0.6
                        ),
                    text=city_data[['City', 'Count']],
                    textposition='top center'
                )
            )

            fig_city_bubbles.update_layout(
                mapbox=dict(
                    style=style,
                    center=dict(lat=51.9194, lon=19.1451), 
                    zoom=6.3,  
                    layers=[{
                        'source': poland_geojson,
                        'type': 'line',
                        'color': border_color,
                        'line': {
                            'width': 1,  
                        }
                    }],
                ),
                geo=dict(
                    showland=True,
                    landcolor=landcolor,
                    showocean=True,
                    oceancolor=oceancolor,
                    showlakes=True,
                    lakecolor=lakecolor,
                    showcountries=True,
                    countrycolor=countrycolor,
                    showcoastlines=True,
                    coastlinecolor=coastlinecolor,
                    projection=dict(type='mercator')
                ),
                template=template, 
                margin=dict(l=0, r=0, t=0, b=0) 
            )
            fig_city_bubbles.write_image(f'{folder_path}/city_bubbles_chart.png', width=1920, height=1080)
            
    if city_pie_chart:
        df_filtered_cities_pie = df_plot.copy() 
        df_filtered_cities_pie['City'] = df_filtered_cities_pie['City'].replace('Warsaw', 'Warszawa')
        df_filtered_cities_pie['City'] = df_filtered_cities_pie['City'].astype(str)
        df_filtered_cities_pie['Latitude'] = df_filtered_cities_pie['Latitude'].astype(str)
        df_filtered_cities_pie['Longitude'] = df_filtered_cities_pie['Longitude'].astype(str)
        df_filtered_cities_pie['City'] = df_filtered_cities_pie['City'].apply(lambda x: x.split(';'))
        df_filtered_cities_pie['Latitude'] = df_filtered_cities_pie['Latitude'].apply(lambda x: x.split(';'))
        df_filtered_cities_pie['Longitude'] = df_filtered_cities_pie['Longitude'].apply(lambda x: x.split(';'))
        
        df_filtered_cities_pie = df_filtered_cities_pie[df_filtered_cities_pie['City'].str.len() == df_filtered_cities_pie['Latitude'].str.len()]
        df_filtered_cities_pie = df_filtered_cities_pie[df_filtered_cities_pie['City'].str.len() == df_filtered_cities_pie['Longitude'].str.len()]

        df_filtered_cities_pie = df_filtered_cities_pie.explode(['City', 'Latitude', 'Longitude'])
        city_counts = df_filtered_cities_pie['City'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']
        top_cities = city_counts.head(10)
        if not top_cities.empty:
            fig_pie_cities = px.pie(
                top_cities, 
                names='City', 
                values='Count', 
                title='City Distribution of Job Offers', 
                labels={'City': 'City', 'Count': 'Count'}, 
                color_discrete_sequence=px.colors.sequential.Viridis,
                template=template
            )
            
            fig_pie_cities.update_layout(
                title=dict(
                    text='City Distribution of Job Offers', 
                    font=dict(size=40), 
                    y=0.93,
                    x=0.02,
                    xanchor='left'
                ),
                legend_title='City', 
                margin=dict(t=50, b=50, l=50, r=50), 
                legend=dict(
                    font=dict(size=30), 
                )
            )
            
            fig_pie_cities.update_traces(
                textinfo='label+percent', 
                textfont=dict(size=25) 
            )
            
            fig_pie_cities.write_image(f'{folder_path}/city_pie_chart.png', width=1920, height=1080)
    
    if languages_bar_chart:
        df_languages_filtered = df_plot[languages.keys()].sum().reset_index()
        df_languages_filtered.columns = ['Language', 'Count']
        df_languages_filtered = df_languages_filtered.sort_values(by='Count', ascending=False)
        
        if not top_cities.empty:
            figure_languages_bar_filtered = px.bar(
                df_languages_filtered, 
                x='Language', 
                y='Count', 
                title='Languages Distribution', 
                labels={'Language': 'Language', 'Count': 'Count'},
                template=template
            )
            
    
            figure_languages_bar_filtered.update_layout(
                title=dict(
                    text='Languages Distribution', 
                    font=dict(size=40), 
                    y=0.95  
                ),
                xaxis_title='',
                yaxis_title='', 
                xaxis=dict(tickfont=dict(size=22)), 
                yaxis=dict(tickfont=dict(size=22)), 
                margin=dict(t=100, b=50, l=50, r=50) 
            )
            
            figure_languages_bar_filtered.write_image(f'{folder_path}/languages_bar_chart.png', width=1920, height=1080)

    if benefits_pie_chart:
        df_benefits_filtered = df_plot[['WorkLifeBalance', 'FinancialRewards', 'HealthWellbeing',
                                            'Development', 'WorkplaceCulture', 'MobilityTransport',
                                            'UniqueBenefits', 'SocialInitiatives']].sum().reset_index()
        df_benefits_filtered.columns = ['Benefit', 'Count']
        
        df_benefits_filtered = df_benefits_filtered.sort_values(by='Count', ascending=False)
        
        if not df_benefits_filtered.empty:
            figure_benefits_pie = px.pie(
                df_benefits_filtered, 
                names='Benefit', 
                values='Count', 
                title='Benefits Distribution',
                labels={'Benefit': 'Benefit', 'Count': 'Count'},
                color_discrete_sequence=px.colors.sequential.Viridis,
                template=template
            )
            
            figure_benefits_pie.update_layout(
                title=dict(
                    text='Benefits Distribution', 
                    font=dict(size=40), 
                    y=0.95,
                    x=0.02,
                    xanchor='left'
                ),
                legend_title='Benefit', 
                margin=dict(t=50, b=50, l=50, r=50),
                    font=dict(size=30) 
            )
            
            figure_benefits_pie.update_traces(
                textinfo='label+percent',  
                textfont=dict(size=25) 
            )
            
            figure_benefits_pie.write_image(f'{folder_path}/benefits_pie_chart.png', width=1920, height=1080)

    if employment_type_pie_chart:
        df_employment_type_filtered = df_plot[['FullTime', 'Hybrid', 'Remote']].sum().reset_index()
        df_employment_type_filtered.columns = ['Employment Type', 'Count']
        
        df_employment_type_filtered = df_employment_type_filtered.sort_values(by='Count', ascending=False)
        
        if not df_benefits_filtered.empty:  
            figure_employment_type_pie = px.pie(
                df_employment_type_filtered, 
                names='Employment Type', 
                values='Count', 
                title='Employment Type Distribution',
                labels={'Employment Type': 'Employment Type', 'Count': 'Count'},
                color_discrete_sequence=px.colors.sequential.Viridis,
                template=template
            )
            
            figure_employment_type_pie.update_layout(
                title=dict(
                    text='Employment Type Distribution', 
                    font=dict(size=40),
                    y=0.95,
                    x=0.02,
                    xanchor='left'
                ),
                legend_title='Employment Type',  
                margin=dict(t=100, b=100, l=100, r=100), 
                legend=dict(
                    font=dict(size=30) 
                ),
                autosize=False,
                width=1920, 
                height=1080,
                showlegend=True
            )
            
            figure_employment_type_pie.update_traces(
                textinfo='label+percent', 
                textfont=dict(size=25), 
            )
            
            figure_employment_type_pie.write_image(f'{folder_path}/employment_type_pie_chart.png', width=1920, height=1080)

    if experience_level_bar_chart:
        df_experiences_filtered = df_plot[['Internship','Junior','Middle','Senior','Lead']].sum().reset_index()
        df_experiences_filtered.columns = ['Experience', 'Count']
        
        df_experiences_filtered = df_experiences_filtered.sort_values(by='Count', ascending=False)
        
        if not df_benefits_filtered.empty:
            figure_experiences_bar_filtered = px.bar(
                df_experiences_filtered, 
                x='Experience', 
                y='Count', 
                title='Experience Level Distribution', 
                labels={'Experience': 'Experience', 'Count': 'Count'},
                template=template
            )
            
            figure_experiences_bar_filtered.update_layout(
                title=dict(
                    text='Experience Level Distribution', 
                    font=dict(size=40),
                    y=0.95
                ),
                xaxis_title='',  
                yaxis_title='', 
                margin=dict(t=100, b=80, l=80, r=50),
                title_x=0.5,  
                autosize=False,
                width=1920, 
                height=1080,
                xaxis=dict(
                    tickfont=dict(size=30)  
                ),
                yaxis=dict(
                    tickfont=dict(size=30) 
                )
            )
            
            figure_experiences_bar_filtered.update_traces(
                marker=dict(
                    line=dict(width=1, color='DarkSlateGrey')
                )
            )
            
            figure_experiences_bar_filtered.write_image(f'{folder_path}/experience_level_bar_chart.png', width=1920, height=1080)

    if salary_box_plot:
        color_map = {
            'Internship': 'blue',
            'Junior': 'orange',
            'Middle': 'red',
            'Senior': 'purple',
            'Lead': 'green'
        }

        figure_salary_boxplot = go.Figure()

        experience_levels = ['Internship', 'Junior', 'Middle', 'Senior', 'Lead']
        colors = [color_map[exp] for exp in experience_levels]
        
        for exp, color in zip(experience_levels, colors):
            df_exp = df_plot[df_plot[exp] == 1]
            df_exp = df_exp[df_exp['Salary'] != 0]
            
            Q1 = df_exp['Salary'].quantile(0.25)
            Q3 = df_exp['Salary'].quantile(0.75)
            IQR = Q3 - Q1

            upper_bound = Q3 + 10 * IQR

            df_exp = df_exp[df_exp['Salary'] <= upper_bound]
                    
            if not df_exp.empty:
                figure_salary_boxplot.add_trace(go.Box(
                    y=df_exp['Salary'],
                    name=f'Salary ({exp})',
                    marker_color=color,
                    boxmean='sd',
                ))

                figure_salary_boxplot.update_layout(
                    title=dict(
                        text='Salary Distribution by Experience Level',
                        font=dict(size=40),
                        y=0.95,
                    ),
                    template=template,
                    xaxis_title='Experience Level',
                    yaxis_title='Salary',
                    boxmode='group',
                    xaxis=dict(tickfont=dict(size=22)),
                    yaxis=dict(tickfont=dict(size=22)),
                    legend=dict(font=dict(size=20))
                )
                figure_salary_boxplot.write_image(f'{folder_path}/salary_box_plot.png', width=1920, height=1080)

    if technologies_bar_chart:
        df_filtered = df_plot.copy()
        all_technologies = df_filtered['Technologies'].astype(str).str.split('[,;]', expand=True).stack()
        all_technologies = all_technologies.astype(str).str.strip().str.upper()
        tech_counts = all_technologies.value_counts().reset_index()
        tech_counts.columns = ['Technology', 'Count']

        tech_counts = tech_counts[tech_counts['Technology'] != 'N/A']

        top_technologies = tech_counts.nlargest(35, 'Count')

        if df_exp.empty:
            print("No data available to figure_technologies_bar.")
        else:        
            figure_technologies_bar = px.bar(
                top_technologies, 
                x='Technology', 
                y='Count', 
                title='Top 35 Most Popular Technologies', 
                labels={'Technology': 'Technology', 'Count': 'Count'},
                template=template
            )

            figure_technologies_bar.update_layout(
                title = dict(
                    font=dict(size=40)
                ),
                xaxis_title='', 
                yaxis_title='',
                xaxis_tickangle=-45
            )
            figure_technologies_bar.update_xaxes(categoryorder='total descending')

            figure_technologies_bar.write_image(f'{folder_path}/technologies_bar_chart.png', width=1920, height=1080)

    if employer_bar_chart:
        employer_counts = df_plot['Employer'].value_counts().reset_index()
        employer_counts.columns = ['Employer', 'Count']
        
        employer_counts = employer_counts.sort_values(by='Count', ascending=False)
        if not employer_counts.empty:
            employer_bar = px.bar(employer_counts.head(25), x='Employer', y='Count', title='Top 50 Employers', template = template)
            
            employer_bar.update_layout(
                title=dict(
                    text='Top 25 Employers By Number Of Job Postings',
                    font=dict(size=40),
                    y=0.95 
                ),
                xaxis_title='', 
                yaxis_title='',  
                margin=dict(t=100, b=80, l=80, r=50), 
                autosize=False,
                width=1920, 
                height=1080, 
                xaxis=dict(
                    tickfont=dict(size=22)
                ),
                yaxis=dict(
                    tickfont=dict(size=22)  
                )
            )
        
            employer_bar.write_image(f'{folder_path}/employer_bar_chart.png', width=1920, height=1080)

    if positions_bar_chart:
        role_counts = df_plot['CoreRole'].value_counts().reset_index()
        role_counts.columns = ['Role', 'Count']
        
        role_counts = role_counts.sort_values(by='Count', ascending=False)
        
        top_roles = role_counts.head(30)
        
        if not top_roles.empty:  
            figure_roles_bar = px.bar(top_roles,
                                    x='Role',
                                    y='Count',
                                    title='Top 30 Roles by Number of Listings',
                                    labels={'Role': 'Role', 'Count': 'Count'},
                                    template=template)
            
            figure_roles_bar.update_layout(
                title=dict(
                    text='Top 30 Roles by Number of Job Postings',
                    font=dict(size=40), 
                    y=0.95 
                ),
                xaxis_title='', 
                yaxis_title='',  
                xaxis_tickangle=45, 
                margin=dict(t=100, b=80, l=80, r=50),  
                autosize=False,
                width=1920, 
                height=1080, 
                xaxis=dict(
                    tickfont=dict(size=22) 
                ),
                yaxis=dict(
                    tickfont=dict(size=22) 
                )
            )
            figure_roles_bar.write_image(f'{folder_path}/positions_bar_chart.png', width=1920, height=1080)

    if post_text:
        post_date = (datetime.now().date() - timedelta(days=1))
        df_plot['DatePosted'] = pd.to_datetime(df_plot['DatePosted'])
        df_plot['Expiration'] = pd.to_datetime(df_plot['Expiration'])
        yesterday_jobs_bot = df_plot[df_plot['DatePosted'].dt.date == post_date].shape[0]
        folder_path = f"figures/{chat_id}"
        os.makedirs(folder_path, exist_ok=True)
        
        if content_daily:
            text_content = f"""
            🌟 Date: {post_date}\n📅 Yesterday's Jobs: {yesterday_jobs_bot}\n📊 Total Jobs in Database: {fetch_data(query, db_config).shape[0]}\nThese jobs can be effectively used for training ML models or performing data analysis.\n😃 Have a nice day!
                """

            text_file_path = os.path.join(folder_path, "summary.txt")
            with open(text_file_path, "w") as text_file:
                text_file.write(text_content)
        else :
            text_file_path = os.path.join(folder_path, "summary.txt")

        
        
def read_image(file_path):
    try:
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        return binary_data
    except FileNotFoundError:
        return None

def insert_figures_and_text(conn, generation_date_with_info, figures, summary_text):
    cursor = conn.cursor()
    insert_query = """INSERT INTO daily_report (
                          generation_id, 
                          benefits_pie_chart, city_bubbles_chart, city_pie_chart, 
                          employer_bar_chart, employment_type_pie_chart, 
                          experience_level_bar_chart, languages_bar_chart, 
                          salary_box_plot, poland_map, positions_bar_chart, 
                          technologies_bar_chart, summary)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      ON CONFLICT (generation_id) 
                      DO UPDATE SET 
                          benefits_pie_chart = EXCLUDED.benefits_pie_chart,
                          city_bubbles_chart = EXCLUDED.city_bubbles_chart,
                          city_pie_chart = EXCLUDED.city_pie_chart,
                          employer_bar_chart = EXCLUDED.employer_bar_chart,
                          employment_type_pie_chart = EXCLUDED.employment_type_pie_chart,
                          experience_level_bar_chart = EXCLUDED.experience_level_bar_chart,
                          languages_bar_chart = EXCLUDED.languages_bar_chart,
                          salary_box_plot = EXCLUDED.salary_box_plot,
                          poland_map = EXCLUDED.poland_map,
                          positions_bar_chart = EXCLUDED.positions_bar_chart,
                          technologies_bar_chart = EXCLUDED.technologies_bar_chart,
                          summary = EXCLUDED.summary"""

    cursor.execute(insert_query, (
        generation_date_with_info, 
        figures.get('benefits_pie_chart'), figures.get('city_bubbles_chart'), figures.get('city_pie_chart'), 
        figures.get('employer_bar_chart'), figures.get('employment_type_pie_chart'), 
        figures.get('experience_level_bar_chart'), figures.get('languages_bar_chart'), 
        figures.get('salary_box_plot'), figures.get('poland_map'), figures.get('positions_bar_chart'), 
        figures.get('technologies_bar_chart'), summary_text
    ))
    
    conn.commit()
    cursor.close()        
    
    
def process_theme(theme_dir, conn, generation_date, theme_type):
    figures = {}
    
    # Check if the directory exists
    if os.path.exists(theme_dir):
        chart_files = ['benefits_pie_chart', 'city_bubbles_chart', 'city_pie_chart', 
                       'employer_bar_chart', 'employment_type_pie_chart', 'experience_level_bar_chart',
                       'languages_bar_chart', 'salary_box_plot', 'poland_map', 
                       'positions_bar_chart', 'technologies_bar_chart']
        
        for chart in chart_files:
            figures[chart] = read_image(os.path.join(theme_dir, f'{chart}.png'))
        
        summary_file_path = os.path.join(theme_dir, "summary.txt")
        with open(summary_file_path, 'r') as file:
            summary_text = file.read()
        generation_date_with_info = f"{generation_date}-{theme_type}"
        insert_figures_and_text(conn, generation_date_with_info, figures, summary_text)
        
        return True
    return False

def save_figures_and_text(base_dir, conn):
    generation_date = str(date.today() - timedelta(days=1))
    figures_dir_light = os.path.join(base_dir, generation_date + "-light")
    figures_dir_dark = os.path.join(base_dir, generation_date + "-dark")

    light_processed = process_theme(figures_dir_light, conn, generation_date, "light")
    dark_processed = process_theme(figures_dir_dark, conn, generation_date, "dark")
    
    try:
        if light_processed:
            shutil.rmtree(figures_dir_light)
            print(f"Directory {figures_dir_light} has been deleted.")
        if dark_processed:
            shutil.rmtree(figures_dir_dark)
            print(f"Directory {figures_dir_dark} has been deleted.")
    except Exception as e:
        print(f"Error deleting directories: {e}")
        
if __name__ == "__main__":
    conn = connect_db(db_config)
    
    df = fetch_data(query_yesterday, db_config)
    
    if not df.empty:
        chat_id = str(date.today() - timedelta(days=1))
        
        generate_figures(df, chat_id + "-light", histogram_day_month_chart=False, map_chart=True, cities_chart=True, 
                         city_pie_chart=True, languages_bar_chart=True, benefits_pie_chart=True, 
                         employment_type_pie_chart=True, experience_level_bar_chart=True, salary_box_plot=True, 
                         technologies_bar_chart=True, employer_bar_chart=True, positions_bar_chart=True, 
                         post_text=True, content_daily=True, light_theme=True)
        
        generate_figures(df, chat_id + "-dark", histogram_day_month_chart=False, map_chart=True, cities_chart=True, 
                         city_pie_chart=True, languages_bar_chart=True, benefits_pie_chart=True, 
                         employment_type_pie_chart=True, experience_level_bar_chart=True, salary_box_plot=True, 
                         technologies_bar_chart=True, employer_bar_chart=True, positions_bar_chart=True, 
                         post_text=True, content_daily=True, light_theme=False)
        
        save_figures_and_text("figures", conn)
    else:
        print("Dataframe is empty -> no uploads for yesterday")
    conn.close()
        