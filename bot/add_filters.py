import pandas as pd
import io
import openpyxl
from datetime import datetime, timedelta

def add_filters_to_df(df, filters, is_excel=False, is_csv=False, is_spark=False):
    filtered_df = df.copy()
    filtered_df['expiration'] = pd.to_datetime(filtered_df['expiration'], errors='coerce')

    if 'experience_level' in filters:
        experience_level = filters['experience_level']
        if experience_level == '🌱 Junior':
            filtered_df = filtered_df[filtered_df['junior'] == 1]
        elif experience_level == '👶 Intern':
            filtered_df = filtered_df[filtered_df['internship'] == 1]
        elif experience_level == '🌿 Middle':
            filtered_df = filtered_df[filtered_df['middle'] == 1]
        elif experience_level == '🌳 Senior':
            filtered_df = filtered_df[filtered_df['senior'] == 1]
        elif experience_level == '🌟 Lead':
            filtered_df = filtered_df[filtered_df['lead'] == 1]

    if 'core_role' in filters:
        core_roles = filters['core_role'].split(';')
        core_roles = [role.strip() for role in core_roles]
        filtered_df = filtered_df[filtered_df['core_role'].apply(
            lambda x: any(role in x for role in core_roles))]

    if 'company' in filters:
        companies = filters['company'].split(';')
        companies = [company.strip() for company in companies]
        filtered_df = filtered_df[filtered_df['company'].apply(
            lambda x: any(role in x for role in core_roles))]
        
    if 'city' in filters:
        cities = filters['city'].split(';')
        cities = [city.strip() for city in cities]
        filtered_df = filtered_df[filtered_df['city'].str.contains('|'.join(cities), case=False, na=False)]

    if 'region' in filters:
        regions = filters['region'].split(';')
        regions = [region.strip() for region in regions]
        filtered_df = filtered_df[filtered_df['region'].str.contains('|'.join(regions), case=False, na=False)]

    if 'language' in filters:
        language_name = filters['language'].split()[0]
        language_col = f"language_{language_name.lower()}"
        if language_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[language_col] == 1]

    if 'work_type' in filters:
        work_types = filters['work_type'].split(';')
        work_types = [work_type.strip() for work_type in work_types]
        filtered_df = filtered_df[
            ((pd.Series('Full-time').isin(work_types)) & (filtered_df['full_time'] == 1)) |
            ((pd.Series('Hybrid').isin(work_types)) & (filtered_df['hybrid'] == 1)) |
            ((pd.Series('Remote').isin(work_types)) & (filtered_df['remote'] == 1))
        ]

    if 'expiration_date' in filters:
        expiration_date = filters['expiration_date']
        yesterday = (datetime.today() - timedelta(days=1)).date()
        yesterday_timestamp = pd.to_datetime(yesterday)
        if expiration_date == 'current':
            filtered_df = filtered_df[filtered_df['expiration'] >= yesterday_timestamp]

    if is_csv:
        filtered_df.drop(columns=['id', 'core_role', 'lat', 'long', 'upload_id'], inplace=True)
        output = io.StringIO()
        filtered_df.to_csv(output, index=False)
        output.seek(0)
        return output.getvalue(), 'csv'

    elif is_excel:
        filtered_df.drop(columns=['id', 'core_role', 'lat', 'long', 'upload_id'], inplace=True)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Filtered Data')
        output.seek(0)
        return output.getvalue(), 'excel'

    elif is_spark:
        filtered_df.drop(columns=['id', 'core_role', 'lat', 'long', 'upload_id'], inplace=True)
        if filtered_df.shape[0] < 15:
            intro_message = f"\nHi there! 😊 Here are the all data based on your criteria for yesterday:\n"
            result_message = intro_message
            for _, row in filtered_df.iterrows():
                result_message += f"📌 {row['job_title']} - {row['employer_name']}   "
                result_message += f"{row['url']}\n"

            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Filtered Data')
            output_excel.seek(0)

            output_csv = io.StringIO()
            filtered_df.to_csv(output_csv, index=False)
            output_csv.seek(0)

            return result_message, output_excel.getvalue(), output_csv.getvalue(), 'text-excel'
        else:
            num_jobs = filtered_df.shape[0]
            result_message = f"Hi, for yesterday we had {num_jobs} jobs based on your criteria: here you go:"

            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Filtered Data')
            output_excel.seek(0)

            output_csv = io.StringIO()
            filtered_df.to_csv(output_csv, index=False)
            output_csv.seek(0)

            return result_message, output_excel.getvalue(), output_csv.getvalue(), 'text-excel'

    else:
        return filtered_df, "pandas"
