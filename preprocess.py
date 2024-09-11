import sys
import os
import re
import numpy as np
import datetime
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
import openpyxl
from tqdm import tqdm
from psycopg2 import sql
import psycopg2
import psycopg2.extras
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from data.dictionaries import (
    contract_values, polish_to_english_months,
    categories_benefits, job_level_dict,
    languages, dict_to_rename, work_type_dict, columns_order, profession_titles,
    translation_dict, not_valid_technologies, keep_technologies
)
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'argos-translate')))

from translate import detect_language, translate_title

import warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

db_config = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD")
}

query = "SELECT * FROM jobs_upload LIMIT 20;"
query_unique_jobs = "SELECT id, technologies_used FROM jobs;"

cities = pd.read_csv("./data/cities_and_regions.csv", sep = ",")

cities_pln = cities['city'].to_list()
cities_eng = cities['city_ascii'].to_list()
admin_name_pln = cities['admin_name'].to_list()
admin_name_eng = cities['admin_name_english'].to_list()


def fetch_data(query, db_config):
    """Establish a database connection and retrieve data."""
    try:
        with psycopg2.connect(**db_config) as conn:
            return pd.read_sql_query(query, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return pd.DataFrame()

df = fetch_data(query, db_config)
df_unique_jobs = fetch_data(query_unique_jobs, db_config)

def replace_underscores(text):
    """Replace special character '▁' with spaces, handling leading/trailing cases."""
    return re.sub(r'^[▁]+|[▁]+$', '', text).replace('▁', ' ')

def process_column(df, column_name, detect_language_func, translate_title_func):
    """Detect and translate language in a specified column, then clean underscores."""
    try:
        print(f"\nProcessing column: '{column_name}'\n")
        tqdm.pandas(desc="Detecting language")
        df['detected_language'] = df[column_name].progress_apply(detect_language_func)
        tqdm.pandas(desc="Translating and cleaning")
        df[column_name] = df.progress_apply(
            lambda row: translate_title_func(row[column_name]) if row['detected_language'] == 'pl' else row[column_name],
            axis=1
        ).apply(replace_underscores)
        print(f"\nFinished processing column: '{column_name}'\n")
    except Exception as e:
        print(f"Error processing column '{column_name}': {e}")
    return df

def convert_to_date(date_str):
    """Convert Polish date strings, dd.mm.yyyy, or relative date descriptions to date objects."""
    if not date_str:
        return pd.NaT

    date_str = date_str.lower().replace('do', '').replace('to', '').strip()
    try:
        return pd.to_datetime(date_str, format='%d.%m.%Y').date()
    except ValueError:
        pass

    match = re.search(r'(\d+)\s*(dni|days)', date_str)
    if match:
        days = int(match.group(1))
        return ((datetime.now() + timedelta(days=days)).date()) - timedelta(days=1)

    for pl_month, en_month in polish_to_english_months.items():
        date_str = date_str.replace(pl_month, en_month)

    converted_date = pd.to_datetime(date_str, format='%d %B %Y', errors='coerce')
    return converted_date.date() if not pd.isna(converted_date) else pd.NaT

def extract_location_info(location):
    cities_found = []
    regions_found = []
    lats_found = []
    longs_found = []
    work_type = "Full Time"
    
    locations = location.split(',')
    
    for loc in locations:
        location_lower = loc.strip().lower()
        city = None
        region = None
        lat = None
        long = None
        
        for c in cities_pln:
            if c.lower() in location_lower:
                city = c
                break
        
        if not city:
            for c in cities_eng:
                if c.lower() in location_lower:
                    city = cities[cities['city_ascii'] == c]['city'].values
                    if len(city) > 0:
                        city = city[0]
                    break
        
        if city:
            if city == "Warsaw":
                city = "Warszawa"
            
            cities_found.append(city)
            
            matching_row = cities[cities['city'] == city]
            
            if not matching_row.empty:
                region = matching_row['admin_name'].values[0]
                lat = matching_row['lat'].values[0]
                long = matching_row['lng'].values[0]
                
                regions_found.append(region)
                lats_found.append(str(lat))
                longs_found.append(str(long))
            
        
        if '"100% time"' in location_lower:
            work_type = "Remote"
        elif any(perc in location_lower for perc in ["70", "50", "40", "30", "20"]):
            work_type = "Hybrid"

    if not cities_found and work_type != "Unknown":
        cities_found = ["Remote"]
        regions_found = ["Remote"]
        lats_found = ["None"]
        longs_found = ["None"]
    
    city = ";".join(cities_found) if cities_found else None
    region = ";".join(regions_found) if regions_found else None
    lat = ";".join(lats_found) if lats_found else None
    long = ";".join(longs_found) if longs_found else None
    
    return pd.Series([city, region, lat, long, work_type], index=['city', 'region', 'lat', 'long', 'work_type'])

def standardize_column(df, column_name, value_map):
    """Standardize categorical values in a specified column."""
    df['standardized'] = df[column_name].map(value_map).fillna(df[column_name])
    return df

def create_category_columns(df, categories, column_name):
    """Create boolean category columns based on standardized values."""
    for category in categories:
        df[category] = df[column_name].apply(lambda x: category in str(x).split(', '))
    return df

def extract_and_convert_salaries(salary_str):
    """Extract start and max salary, convert net to gross, and convert hourly to monthly."""
    salary_str = salary_str.replace(',', ' ')
    salary_str = re.sub(r'(\d)\s+(\d)', r'\1\2', salary_str)
    parts = salary_str.split()
    normalized_parts = []
    for i, part in enumerate(parts):
        if i > 0 and part.isdigit() and parts[i-1].isdigit():
            normalized_parts[-1] += part 
        else:
            normalized_parts.append(part)
    return ' '.join(normalized_parts)

def extract_and_convert_salaries(salary_str):
    salary_str = salary_str.replace(',', ' ')
    salary_str = re.sub(r'(\d)\s+(\d)', r'\1\2', salary_str)
    parts = salary_str.split()
    
    normalized_parts = []
    for i, part in enumerate(parts):
        if i > 0 and part.isdigit() and parts[i-1].isdigit():
            normalized_parts[-1] += part  
        else:
            normalized_parts.append(part)
    
    salary_str = ' '.join(normalized_parts)
    dash_pos = salary_str.find('–')
    if dash_pos == -1:
        return pd.Series(['0', '0'])

    first_part = salary_str[:dash_pos].strip()
    second_part = salary_str[dash_pos + 1:].split()[0].strip()
    
    salary_types = ["gross", "net", "brutto", "netto"]
    salary_str_lower = salary_str.lower()
    
    salary_to_pos = {}
    for salary_type in salary_types:
        pos = salary_str_lower.find(salary_type)
        if pos != -1:
            salary_to_pos[salary_type] = pos
        
    def get_numeric_value(salary_str):
        if not salary_str:
            return 0
        return int(re.sub(r'\D', '', salary_str))
    
    start_salary = get_numeric_value(first_part)
    max_salary = get_numeric_value(second_part)
    
    is_netto = any(salary_type in salary_to_pos for salary_type in ["net", "netto"])
    is_hourly = (start_salary and start_salary < 1000) or (max_salary and max_salary < 1000)
    
    tax_rate = 0.23
    if is_netto:
        if start_salary:
            start_salary = start_salary / (1 - tax_rate)
        if max_salary:
            max_salary = max_salary / (1 - tax_rate)
    
    if is_hourly:
        if start_salary and start_salary < 1000:
            start_salary *= 160
        if max_salary and max_salary < 1000:
            max_salary *= 160
                
    return pd.Series([start_salary, max_salary])

def assign_benefit_categories(df):
    """Assign benefits to categories."""
    for category, keywords in categories_benefits.items():
        df[category] = df['benefits'].apply(lambda benefit: any(keyword.lower() in benefit.lower() for keyword in keywords))
    return df

def update_categories(df, text_columns, categories_dict, column_name):
    """Update categories based on the presence of keywords in text columns."""
    for category, keywords in categories_dict.items():
        df[category] = df[text_columns].apply(
            lambda x: int(any(
                any(keyword.lower() in str(x[col]).lower() for col in text_columns) for keyword in keywords
            )),
            axis=1
        )
    return df

def map_job_level(job_level_description):
    """Map job level description to predefined job levels."""
    return job_level_dict.get(job_level_description)

def extract_job_role(title):
    """Extract and clean job role from the given title and match it against a predefined list using TF-IDF."""
    if not title:
        return None
    
    title = title.lower()
    remove_terms = ['junior', 'middle', 'senior', 'programmist', 'lead', 'team leader', 'team lead']
    for term in remove_terms:
        title = title.replace(term, '')
    
    title = re.sub(r'\[.*?\]|\(.*?\)', '', title)
    title = re.sub(r' with.*', '', title)
    title = re.sub(r'[|\\].*', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    
    words = title.split()
    cleaned_title = ' '.join([word.upper() if len(word) <= 3 else word.title() for word in words])
    
    lowercase_titles = [t.lower() for t in profession_titles]
    
    vectorizer = TfidfVectorizer().fit_transform([cleaned_title] + lowercase_titles)
    cosine_sim = cosine_similarity(vectorizer[0:1], vectorizer[1:])
    closest_index = cosine_sim.argmax()
    
    similarity_score = cosine_sim[0][closest_index]
    if similarity_score > 0.7:
        return profession_titles[closest_index]
    else:
        return cleaned_title.title()

if df.empty:
    print("We don't have new jobs.")
    sys.exit() 
    
df[['city', 'region', 'lat', 'long', 'work_type']] = df['location'].apply(extract_location_info)
df['expiration'] = df['expiration'].apply(convert_to_date)

df['id'] = df['job_title'] + "_" + df['employer_name'] + "_" + df['city'] + "_" + df['expiration'].astype(str)
df = df.drop_duplicates(subset='id')

unique_ids = set(df_unique_jobs['id'])
df = df[~df['id'].isin(unique_ids)]
    
def replace_polish_words(text, translation_dict):
    words = text.split()
    translated_words = [translation_dict.get(word.lower(), word) for word in words]
    return ' '.join(translated_words)

columns_to_process = ['job_title','responsibilities','requirements','benefits','offering']

for column in columns_to_process:
    df = process_column(df, column, detect_language, translate_title)

# Apply the translation function to replace Polish words with English equivalents
for column in columns_to_process:
    df[column] = df[column].apply(lambda x: replace_polish_words(str(x), translation_dict))

df['core_role'] = df['job_title'].apply(extract_job_role)

df['hybryd_full_remote'] = df['hybryd_full_remote'].fillna(df['work_type'])
df['hybryd_full_remote'] = df['hybryd_full_remote'].replace("N/A", np.nan)  # Replace "N/A" with NaN
df['hybryd_full_remote'] = df['hybryd_full_remote'].fillna(df['work_type']) 
df['hybryd_full_remote'] = df['hybryd_full_remote'].str.replace(" • ", ",", regex=False)


df[['start_salary', 'max_salary']] = df['salary'].apply(extract_and_convert_salaries)
 
df = assign_benefit_categories(df)

contract_categories = [
    'B2B Contract', 'Contract of Employment', 'Contract of Mandate', 'Substitution Agreement',
    'Contract of Work', 'Agency Agreement', 'Temporary Staffing Agreement',
    'Contract for Specific Work', 'Internship / Apprenticeship Contract', 'Contract of Temporary Employment'
]
df = standardize_column(df, 'contract_type', contract_values)
df = create_category_columns(df, contract_categories, 'standardized')
df = update_categories(df, ['job_title', 'technologies', 'responsibilities', 'requirements', 'offering'], languages, 'languages')
df['job_level'] = df['experience_level'].apply(map_job_level)
job_levels = ['internship', 'junior', 'middle', 'senior', 'lead']
df = create_category_columns(df, job_levels, 'job_level')

def custom_title_case(text):
    words = text.split()
    formatted_words = [word.upper() if len(word) <= 3 else word.capitalize() for word in words]
    return ' '.join(formatted_words)

df['employer_name'] = (
    df['employer_name']
    .str.replace(r"\b(SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ|SPÓŁKA KOMANDYTOWA|Spółka Akcyjna|S[.]?\s?A[.]?|Sp[.]?\s?J[.]?|sp[.]?\s?z[.]?\s?o[.]?\s?o[.]?|spzoo|sp\.?z\.?o\.?|\bSP ZOO\b|\bPL\b|\[|\])\b", "", case=False, regex=True)
    .str.replace(r"\b(Polska|Poland|ltd[.]?|gmbh)\b", "", case=False, regex=True)
    .str.replace(r"\.\s*|^\s*|\s+$", " ", regex=True) 
    .str.replace(r"\s+", " ", regex=True)  
    .str.replace("()","")
    .str.strip()
    .apply(custom_title_case) 
)

df['normalized_name'] = df['employer_name'].str.lower()

def consolidate_names(series):
    all_names = series.unique()
    name_map = {}
    
    for name in all_names:
        for other_name in all_names:
            if name != other_name and name in other_name:
                name_map[name] = other_name
                break
                
    return series.map(lambda x: name_map.get(x, x))

df['employer_name'] = consolidate_names(df['employer_name'])
df = df.drop(columns=['normalized_name'])

df.drop(columns=['standardized',
                 'location', 'salary', 'job_level'], inplace=True)
df.replace({"TRUE": 1, "FALSE": 0, True: 1, False: 0}, inplace=True)
df.rename(columns=dict_to_rename, inplace=True)

df["expiration"] = pd.to_datetime(df["expiration"])

df.drop(columns="work_type", inplace=True)

df['technologies_used'] = df['technologies_used'].str.upper()

technologies_set = set()

for technologies in df['technologies_used']:
    if technologies != 'N/A':
        techs = [tech.strip() for tech in technologies.replace(';', ',').split(',')]
        techs = [tech for tech in techs if len(tech) >= 2]
        technologies_set.update(techs)

for technologies in df_unique_jobs['technologies_used']:
    if technologies != 'N/A':
        techs = [tech.strip() for tech in technologies.replace(';', ',').split(',')]
        techs = [tech for tech in techs if len(tech) >= 2]
        technologies_set.update(techs)

updated_technologies = []

def is_technology_present(text, tech):
    words = text.lower().split()
    return tech.lower() in words

for index, row in df.iterrows():    
    if row["technologies_used"] == "N/A":
        new_technologies = []
    else:
        existing_techs = set(row["technologies_used"].split(';'))
        new_technologies = list(existing_techs)
    
    for tech in technologies_set:
        tech_lower = tech.lower()
        if ((is_technology_present(row["job_requirements"], tech) or 
             is_technology_present(row["worker_responsibilities"], tech) or 
             is_technology_present(row["job_title"], tech)) and \
            ((len(tech) > 2) or (tech in keep_technologies)) and \
            (tech not in not_valid_technologies)):
            if tech not in new_technologies:
                new_technologies.append(tech)
    
    updated_technologies.append(';'.join(new_technologies) if new_technologies else 'N/A')

df['technologies_used'] = updated_technologies

df = df.dropna(subset=['expiration'])

for column in df.columns:
    if df[column].isna().any():
        print(f"There are NaT values in the {column} column.")

for category, keywords in work_type_dict.items():
    df[category] = df['hybryd_full_remote'].apply(lambda x: int(any(keyword in str(x).lower() for keyword in keywords)))

df.drop(columns=['hybryd_full_remote', 'contract_type', 'experience_level', 'detected_language'], inplace=True)
df = df[columns_order]
df['date_posted'] = df['date_posted']

## Output to files
# now = datetime.now()
# one_day_before = now - timedelta(days=1)
# timestamp = one_day_before.strftime("%Y%m%d_%H%M%S")
# df.to_excel(f"data/output_{timestamp}.xlsx", index=False, engine="openpyxl")

def insert_data_to_db(df, table_name, db_config):
    """Insert data from DataFrame into the specified table in PostgreSQL."""
    with psycopg2.connect(**db_config) as conn:
        cur = conn.cursor()

        columns = df.columns
        values = [tuple(x) for x in df.to_numpy()]
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns))
        )                    
        
        psycopg2.extras.execute_values(
            cur, insert_query, values, template=None, page_size=100
        )
        conn.commit()
        print(f"Data inserted into table {table_name}")

insert_data_to_db(df, 'jobs', db_config)