import os
import pandas as pd
import psycopg2
from dash import Dash, html, dcc
import plotly.express as px
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

db_config = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD")
}

if not db_config['password']:
    raise ValueError("DB_PASSWORD environment variable is not set")

def fetch_data(query, db_config):
    """Establish a database connection and retrieve data."""
    try:
        with psycopg2.connect(**db_config) as conn:
            return pd.read_sql_query(query, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return pd.DataFrame()

# Define the query
query = "SELECT * FROM jobs;"

# Fetch data
df = fetch_data(query, db_config)

# Check if dataframe is empty
if df.empty:
    print("No data retrieved from the database.")
    sys.exit()

# Calculate the average salary as the mean of min_salary and max_salary
df['salary'] = (df['start_salary'] + df['max_salary']) / 2

# Group by core_role and calculate average salary
avg_salary_by_role = df.groupby('core_role')['salary'].mean().reset_index()

# Sort and select top 30 roles by average salary
top_30_roles = avg_salary_by_role.sort_values(by='salary', ascending=False).head(30)

# Filter the original dataframe for these top 30 roles
df_top_30 = df[df['core_role'].isin(top_30_roles['core_role'])]

# Remove outliers using IQR
Q1 = df_top_30['salary'].quantile(0.25)
Q3 = df_top_30['salary'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df_filtered = df_top_30[(df_top_30['salary'] >= lower_bound) & (df_top_30['salary'] <= upper_bound)]

# Calculate average salary for each core_role (filtered)
avg_salary_filtered = df_filtered.groupby('core_role')['salary'].mean().reset_index()

# Bar plot: Average salary by core_role for top 30 roles without outliers
fig1 = px.bar(avg_salary_filtered, x='core_role', y='salary',
              title='Average Salary by Core Role (Top 30, Without Outliers)',
              labels={'core_role': 'Core Role', 'salary': 'Average Salary'},
              color='core_role')

# Update layout for a simple Plotly theme
fig1.update_layout(
    xaxis_title='Core Role',
    yaxis_title='Average Salary',
    xaxis_tickangle=-45,
    title_font_size=22,
    title_x=0.5,
    font=dict(size=12)
)

# Initialize Dash app
app = Dash(__name__)

# Dash layout
app.layout = html.Div(style={'padding': '10px'}, children=[
    html.H1(children='Top 30 Core Roles by Average Salary (Without Outliers)', style={'textAlign': 'center'}),
    dcc.Graph(
        id='avg-salary-by-role',
        figure=fig1
    ),
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)