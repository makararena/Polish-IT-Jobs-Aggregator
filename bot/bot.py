import os
import re
import sys
import json
import asyncio
import smtplib
import signal
import asyncpg
import warnings
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from fuzzywuzzy import process
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor

# Custom imports
from add_filters import add_filters_to_df
from generate_figures import generate_figures

# Load data from different files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.dictionaries import (
    PROJECT_DESCRIPTION, WELCOME_MESSAGE, lAGUAGE_OPTIONS
)
from data.queries import (
    INSERT_USER_DATA_QUERY, DELETE_USER_DATA_QUERY, CHECK_IF_USER_EXIST_QUERY, 
    INSERT_USER_DATA_BEFORE_EXIT_QUERY, LOAD_USER_DATA_QUERY, ALL_JOBS_QUERY, 
    YESTERDAY_JOBS_QUERY, GET_FILTERS_QUERY, LOAD_ALL_PLOTS_QUERY, 
    GET_CLOSEST_DATE_QUERY, INSERT_USER_REVIEW_QUERY
)

warnings.filterwarnings("ignore", message="Using slow pure-python SequenceMatcher")
warnings.simplefilter("ignore")

# Load environment variables
load_dotenv()

# Change current directory to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Telegram bot setup
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def fetch_data(query):
    """Fetch data from the database using the SQLAlchemy engine."""
    try:
        return pd.read_sql_query(query, engine)
    except Exception as e:
        print(f"Error fetching data from PostgreSQL database: {e}")
        return pd.DataFrame()

# Database connection setup
db_config = json.loads(os.getenv("DB_CONFIG"))
conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
engine = create_engine(conn_str)

df = fetch_data(ALL_JOBS_QUERY)

FIGURES_PATH = './figures'

WAITING_FOR_FILTERS = 'waiting_for_filters'
WAITING_FOR_EXPERIENCE = 'waiting_for_experience'
WAITING_FOR_CORE_ROLE = 'waiting_for_core_role'
WAITING_FOR_WORK_TYPE = 'waiting_for_work_type'
WAITING_FOR_LANGUAGE = 'waiting_for_language'
WAITING_FOR_ANOTHER_DATE = 'waiting_for_another_date'
WAITING_FOR_REVIEW = 'waiting_for_review'
WAITING_FOR_RATING = 'waiting_for_rating'
WAITING_FOR_NOTIFICATION_TIME = 'waiting_for_notification_time'
WAITING_FOR_DAILY_UPDATE_CONFIRMATION = 'waiting_for_daily_update_confirmation'
WAITING_FOR_COMPANY = 'waiting_for_company'
WAITING_FOR_CITY = 'waiting_for_city'
WAITING_FOR_REGION = 'waiting_for_region'
WAITING_FOR_CITY_INPUT = 'waiting_for_city_input'
WAITING_FOR_CORE_ROLE_INPUT = 'waiting_for_core_role_input'
WAITING_FOR_COMPANY_INPUT = 'waiting_for_company_input'
WAITING_FOR_DATA_FORMAT = 'waiting_for_data_format'
WAITING_CURRENT_FILTERS = 'waiting_current_filters'
WAITING_RESET_DAILY_UPDATE = 'waiting_reset_daily_update'
WAITING_FOR_ANOTHER_THEME = 'waiting_for_another_theme' 
WAITING_FOR_EMAIL = 'waiting_for_email'

WAITING_FOR_ACTION_AFTER_FILTER = 'waiting_for_action_after_filter'


user_states = {}
user_filters = {}
user_subscriptions = {}




def insert_user_data(user_id, filters):
    """Insert user data into the database."""
    insert_query = INSERT_USER_DATA_QUERY
    try:
        with engine.connect() as connection:
            connection.execute(
                text(insert_query),
                {
                    'user_id': user_id,
                    'filters': filters
                }
            )
    except Exception as e:
        print(f"Error inserting data into PostgreSQL database: {e}")
        
def delete_user_data(user_id):
    """Delete user data from the database based on user_id."""
    delete_query = DELETE_USER_DATA_QUERY
    try:
        with engine.connect() as connection:
            connection.execute(
                text(delete_query),
                {'user_id': user_id}
            )
        print(f"User data for user_id {user_id} has been deleted.")
    except Exception as e:
        print(f"Error deleting data from PostgreSQL database: {e}")
        
def user_exists(user_id):
    """Check if a user exists in the database based on user_id."""
    select_query = CHECK_IF_USER_EXIST_QUERY
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(select_query),
                {'user_id': user_id}
            ).fetchone()
        return result is not None
    except Exception as e:
        print(f"Error checking user existence in PostgreSQL database: {e}")
        return False
    
def save_user_data_before_exit(chat_id, state, filters):
    """Save user data before exit."""
    state_json = json.dumps(state)
    filters_json = json.dumps(filters)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(INSERT_USER_DATA_BEFORE_EXIT_QUERY),
                {'chat_id': chat_id, 'state': state_json, 'filters': filters_json}
            )
        print("Data inserted/updated successfully.")
    except Exception as e:
        print(f"Error saving user data: {e}")


async def load_all_user_data():
    """Load all user data from the database into memory."""
    conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    
    try:
        conn = await asyncpg.connect(dsn=conn_str)
        select_query = LOAD_USER_DATA_QUERY
        rows = await conn.fetch(select_query)
        for row in rows:
            chat_id = row['chat_id']
            state = row['state']
            filters = row['filters']

            user_states[chat_id] = json.loads(state) if state else {}
            user_filters[chat_id] = json.loads(filters) if filters else {}
        
        await conn.close()

    except Exception as e:
        print(f"Error loading user data from PostgreSQL database: {e}")
        
async def check_and_post_files(chat_id, date_str):
    """Check for available files in the database on the given date and send them to the user."""
    query = LOAD_ALL_PLOTS_QUERY
    try:
        with await asyncio.get_event_loop().run_in_executor(None, lambda: engine.connect()) as connection:
            result = connection.execute(text(query), {'date_str': date_str}).fetchone()

            if result:
                images = {
                    'benefits_pie_chart': result['benefits_pie_chart'],
                    'city_bubbles_chart': result['city_bubbles_chart'],
                    'city_pie_chart': result['city_pie_chart'],
                    'employer_bar_chart': result['employer_bar_chart'],
                    'employment_type_pie_chart': result['employment_type_pie_chart'],
                    'experience_level_bar_chart': result['experience_level_bar_chart'],
                    'languages_bar_chart': result['languages_bar_chart'],
                    'salary_box_plot': result['salary_box_plot'],
                    'poland_map': result['poland_map'],
                    'positions_bar_chart': result['positions_bar_chart'],
                    'technologies_bar_chart': result['technologies_bar_chart']
                }
                
                summary_text = result['summary']
                
                for chart_name, image_data in images.items():
                    if image_data:
                        try:
                            await bot.send_photo(chat_id, image_data)
                        except Exception as e:
                            print(f"Error sending image {chart_name}: {e}")
                
                if summary_text:
                    try:
                        await bot.send_message(chat_id, summary_text)
                    except Exception as e:
                        print(f"Error sending summary text: {e}")
            else:
                closest_date_query = GET_CLOSEST_DATE_QUERY
                closest_date_result = connection.execute(text(closest_date_query), {'date_str': date_str}).fetchone()
                
                if closest_date_result:
                    closest_date = closest_date_result['generation_id']
                    await bot.send_message(
                            chat_id, 
                            f"❌ No data found for {date_str.replace('-dark', '').replace('-light', '')}. "
                            f"The closest available date is 📅 {closest_date.replace('-dark', '').replace('-light', '')}.\n\n"
                            "👉 If you want to get data for this date, please type: "
                            f"`{closest_date.replace('-dark', '').replace('-light', '')}` or type another date after this one."
                        )
                else:
                    await bot.send_message(chat_id, f"No data found for {date_str.replace('-dark', '').replace('-light', '')}, and no other available dates.")
    except Exception as e:
        print(f"Error querying the database: {e}")
        
async def send_start_message(chat_id, to_send_message=True):
    """Send a welcome message with options to the user."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    view_yesterday_button = types.KeyboardButton("Yesterday's Jobs")
    view_anotherdate_button = types.KeyboardButton("Jobs by Date")
    about_project_button = types.KeyboardButton("About Project")
    add_filters_button = types.KeyboardButton("Set Filters 🔍")
    leave_review_button = types.KeyboardButton("Feedback ✍️")
    reset_daily_update_button = types.KeyboardButton("Reset Daily Update ❌")
    change_graph_theme_button = types.KeyboardButton("Change Graph Theme 🎨")
    
    markup.add(add_filters_button, view_yesterday_button, view_anotherdate_button)
    markup.add(about_project_button, leave_review_button, reset_daily_update_button)
    markup.add(change_graph_theme_button)
    
    if to_send_message:
        await bot.send_message(chat_id, WELCOME_MESSAGE, reply_markup=markup)
    else:
        await bot.send_message(chat_id, "🎉 Welcome Back to the Main Menu! 🎉", reply_markup=markup)
    
async def send_project_info(chat_id):
    """Send project description to the user."""
    await bot.send_message(chat_id, PROJECT_DESCRIPTION, parse_mode='Markdown')

async def handle_review_submission(message: types.Message):
    """Handle user review submission."""
    chat_id = message.chat.id
    review = message.text
    username = message.from_user.username
    user_name = message.from_user.full_name
    chat_type = message.chat.type

    print(f"Received review from {chat_id}: {review} by {username} ({user_name}), Chat type: {chat_type}")

    rating_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    rating_buttons = [
        types.KeyboardButton("👎 Bad"),
        types.KeyboardButton("😐 Okay"),
        types.KeyboardButton("🙂 Good"),
        types.KeyboardButton("👍 Very Good"),
        types.KeyboardButton("🌟 Excellent")
    ]
    rating_keyboard.add(*rating_buttons)

    await bot.send_message(
        chat_id,
        "Thank you for your review! How would you rate your experience?",
        reply_markup=rating_keyboard
    )

    user_states[chat_id] = WAITING_FOR_RATING
    user_filters[chat_id] = {
        'review': review,
        'username': username,
        'user_name': user_name,
        'chat_type': chat_type
    }
        
async def check_column_and_suggest(message: types.Message, column_name: str, name: str):
    chat_id = message.chat.id
    input_value = message.text

    column_list = df[column_name].tolist()
    all_values = set()

    for values in column_list:
        all_values.update(values.split(';'))

    if input_value in all_values:
        current_value = user_filters.setdefault(chat_id, {}).get(column_name, '')
        if current_value:
            user_filters[chat_id][column_name] = f"{current_value};{input_value}"
        else:
            user_filters[chat_id][column_name] = input_value
        await bot.send_message(chat_id, f"Added filter for {column_name.replace('_', ' ').capitalize()}: {input_value.capitalize()}")
        await post_filter_action_options(chat_id)
    else:
        similar_values = process.extract(input_value, all_values, limit=10)
        suggestions = [value[0] for value in similar_values]
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for value in suggestions:
            button = types.KeyboardButton(value)
            markup.add(button)
        
        exit_button = types.KeyboardButton("Back ⬅️")
        markup.add(exit_button)

        def modify_column_name(name):
            if name.endswith('y'):
                return name[:-1] + 'ie'
            return name

        modified_column_name = modify_column_name(column_name)

        await bot.send_message(
            chat_id,
            f"No exact match found. 🤔 Here are some similar {modified_column_name.replace('_', ' ')}s you might be interested in:\n👇 Please select one of the options below or click 'Back' to exit.",
            reply_markup=markup,
        )
        user_states[chat_id] = name
        
async def handle_rating_submission(message: types.Message):
    """Handle user rating submission."""
    chat_id = message.chat.id
    rating = message.text

    text_to_number = {
        "👎 Bad": 1,
        "😐 Okay": 2,
        "🙂 Good": 3,
        "👍 Very Good": 4,
        "🌟 Excellent": 5
    }

    if rating in text_to_number:
        rating_value = text_to_number[rating]

        review_data = user_filters.get(chat_id, {})
        review = review_data.get('review', '')
        username = review_data.get('username', '')
        user_name = review_data.get('user_name', '')
        chat_type = review_data.get('chat_type', '')

        insert_query = INSERT_USER_REVIEW_QUERY
        try:
            with engine.connect() as connection:
                connection.execute(
                    text(insert_query),
                    {
                        'chat_id': chat_id,
                        'username': username,
                        'user_name': user_name,
                        'review': review,
                        'rating': rating_value,
                        'review_type': 'feedback',
                        'chat_type': chat_type
                    }
                )
            await bot.send_message(chat_id, "Thank you for your rating!")
            await start_command(message)
        except Exception as e:
            print(f"Error saving review and rating to PostgreSQL database: {e}")
            await bot.send_message(chat_id, "An error occurred while saving your review and rating. Please try again later.")

        user_states[chat_id] = None
        user_filters[chat_id] = {}
    else:
        await bot.send_message(chat_id, "Invalid rating. Please select one of the options.")

       
async def handle_filters(message: types.Message):
    """Send a message asking the user which filters they want to apply."""
    chat_id = message.chat.id

    # Define buttons
    experience_button = types.KeyboardButton("Experience Level 💼")
    core_role_button = types.KeyboardButton("Role 🎯")
    company_button = types.KeyboardButton("Company 🏢")
    city_button = types.KeyboardButton("City 🌆")
    region_button = types.KeyboardButton("Region 🌍")
    language_button = types.KeyboardButton("Language 🗣️")
    work_type_button = types.KeyboardButton("Work Type 💻")
    data_type_button = types.KeyboardButton("Use Only Current Data 📅")
    clear_filters_button = types.KeyboardButton("Clear Filters 🗑️")
    check_filters_button = types.KeyboardButton("Current Filters 🔍")
    main_menu_button = types.KeyboardButton("Back ⬅️")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(experience_button, core_role_button, 
                company_button, city_button, 
                region_button, language_button, 
                work_type_button, clear_filters_button)

    if 'expiration_date' in user_filters.get(chat_id, {}):
        data_type_button = types.KeyboardButton("Use All Data 🔄")
    markup.add(data_type_button)
    
    markup.add(check_filters_button, main_menu_button)
    
    await bot.send_message(chat_id, "What would you like to filter by?", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_FILTERS

async def handle_experience_selection(message: types.Message):
    """Send a message asking the user to select their experience level."""
    chat_id = message.chat.id
    experience_levels = ["👶 Intern", "🌱 Junior", "🌿 Middle", "🌳 Senior", "🌟 Lead"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(exp) for exp in experience_levels]
    exit_button = types.KeyboardButton("Back ⬅️")
    markup.add(*buttons, exit_button)
    
    await bot.send_message(chat_id, "Select the experience level you want to filter by:", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_EXPERIENCE

    
async def handle_core_role_selection(message: types.Message):
    """Send a message asking the user to select or input a core role."""
    chat_id = message.chat.id
    top_roles = df['core_role'].value_counts().nlargest(50).index.tolist()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(role) for role in top_roles]
    other_button = types.KeyboardButton("Other 🔄")
    exit_button = types.KeyboardButton("Back ⬅️")
    markup.add(*buttons, other_button, exit_button)
    
    await bot.send_message(chat_id, "Select the core role you want to filter by or type your own:", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_CORE_ROLE
    
async def handle_work_type_selection(message: types.Message):
    """Send a message asking the user to select a work type."""
    chat_id = message.chat.id
    work_types = ["Full-time", "Hybrid", "Remote"] 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(work_type) for work_type in work_types]
    exit_button = types.KeyboardButton("Back ⬅️")  
    markup.add(*buttons, exit_button)  
    await bot.send_message(chat_id, "Select the work type you want to filter by:", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_WORK_TYPE
           
       
async def confirm_daily_update(message: types.Message):
    """Send current filters and ask for confirmation to apply for daily updates."""
    chat_id = message.chat.id
    filters = user_filters.get(chat_id, {})
    
    if filters:
        filters_info = ""
        for key, value in filters.items():
            if key not in {"graph_theme", "notification_time", "email"} and value:
                filters_info += f"{key.replace('_', ' ').capitalize()}: {value}\n"

        if filters_info:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            confirm_button = types.KeyboardButton("Yes, apply for Daily Updates ✅")
            back_button = types.KeyboardButton("Back ⬅️")
            
            markup.add(confirm_button, back_button)

            await bot.send_message(
                chat_id, 
                f"Your current filters are:\n{filters_info}\nAre you sure you want to apply for daily updates?", 
                reply_markup=markup
            )
            
            user_states[chat_id] = WAITING_FOR_DAILY_UPDATE_CONFIRMATION
        else:
            await bot.send_message(
                chat_id,
                "You don't have any valid filters set. Please set your filters first."
            )
            await handle_filters(message)

    else:
        await bot.send_message(
            chat_id,
            "You don't have any filters set. Please set your filters first."
        )
        await handle_filters(message)

    
async def post_filter_action_options(chat_id):
    """Send options for next actions after a filter is applied."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    add_another_button = types.KeyboardButton("Add Filter 🚀")
    download_data_button = types.KeyboardButton("Download Data ⬇️")
    check_graphs_button = types.KeyboardButton("Check Graphs 📊")
    check_filters_button = types.KeyboardButton("Current Filters 🔍")
    clear_filters_button = types.KeyboardButton("Clear Filters 🗑️")
    apply_daily_update_button = types.KeyboardButton("Apply for Daily Update 📅")  
    back_button = types.KeyboardButton("Back ⬅️")  
    
    markup.add(add_another_button, download_data_button, check_graphs_button, check_filters_button, clear_filters_button)
    markup.add(apply_daily_update_button) 
    markup.add(back_button)  

    await bot.send_message(
        chat_id,
        "What would you like to do next?",
        reply_markup=markup
    )
    
    user_states[chat_id] = WAITING_FOR_ACTION_AFTER_FILTER


async def handle_company_selection(message: types.Message):
    """Send a message asking the user to select a company."""
    chat_id = message.chat.id
    companies = df['employer_name'].value_counts().nlargest(50).index.tolist()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(company) for company in companies]
    other_button = types.KeyboardButton("Other 🔄")
    exit_button = types.KeyboardButton("Back ⬅️")
    markup.add(*buttons, other_button, exit_button)
    await bot.send_message(chat_id, "Select the company you want to filter by:", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_COMPANY

async def handle_clear_filters(chat_id):
    """Clear the current filters for the user."""
    user_filters[chat_id] = {}  
    await bot.send_message(chat_id, "All your filters have been cleared.")
    await post_filter_action_options(chat_id) 
    
async def handle_city_selection(message: types.Message):
    """Send a message asking the user to select a city."""
    chat_id = message.chat.id
    all_cities = df['city'].str.split(';').explode()

    cities = all_cities.value_counts().nlargest(50).index.tolist()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(city) for city in cities]
    other_button = types.KeyboardButton("Other 🔄")
    exit_button = types.KeyboardButton("Back ⬅️")
    markup.add(*buttons, other_button, exit_button)
    
    await bot.send_message(chat_id, "Select the city you want to filter by:", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_CITY
    
async def handle_region_selection(message: types.Message):
    """Send a message asking the user to select a region."""
    chat_id = message.chat.id
    polish_regions = [
        "Dolnośląskie", "Kujawsko-Pomorskie", "Lubelskie", "Lubuskie", 
        "Łódzkie", "Małopolskie", "Mazowieckie", "Opolskie", 
        "Podkarpackie", "Podlaskie", "Pomorskie", "Śląskie", 
        "Świętokrzyskie", "Warmińsko-Mazurskie", "Wielkopolskie", "Zachodniopomorskie", "Remote"
    ]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(region) for region in polish_regions]
    exit_button = types.KeyboardButton("Back ⬅️")
    markup.add(*buttons, exit_button)
    await bot.send_message(chat_id, "Select the region you want to filter by:", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_REGION

    
async def handle_language_selection(message: types.Message):
    """Send a message asking the user to select a language."""
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(language) for language in lAGUAGE_OPTIONS]
    exit_button = types.KeyboardButton("Back ⬅️")
    markup.add(*buttons, exit_button)
    await bot.send_message(chat_id, "Select the language you want to filter by:", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_LANGUAGE

async def handle_download_filtered_data(message: types.Message):
    """Handle the download of filtered data."""
    chat_id = message.chat.id
    filters = user_filters.get(chat_id, {})
    
    filtered_data, file_type = add_filters_to_df(df, filters, is_excel=False, is_csv=False)
    
    if filtered_data.empty:
        await bot.send_message(chat_id, "Sorry, but we don't have data based on your filter. 🚫")
        await post_filter_action_options(chat_id)
    else :
        if not filters:
                await bot.send_message(chat_id, "⚠️ Please note that you have not applied any filters, so you will receive all information for all time.")
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        csv_button = types.KeyboardButton("CSV")
        excel_button = types.KeyboardButton("Excel")
        exit_button = types.KeyboardButton("Back ⬅️")
        markup.add(csv_button, excel_button, exit_button)

        await bot.send_message(chat_id, "In which format would you like to receive the filtered data?", reply_markup=markup)
        user_states[chat_id] = WAITING_FOR_DATA_FORMAT

async def handle_data_format_selection(message: types.Message):
    """Handle the selection of data format (CSV or Excel) for downloading."""
    chat_id = message.chat.id
    format_choice = message.text

    if format_choice in ["CSV", "Excel"]:
        filters = user_filters.get(chat_id, {})
        is_csv = format_choice == "CSV"
        is_excel = format_choice == "Excel"
        
        filtered_data, file_type = add_filters_to_df(df, filters, is_excel=is_excel, is_csv=is_csv)

        if file_type == 'csv':
            await bot.send_document(chat_id, (f'filtered_data.csv', filtered_data))
        elif file_type == 'excel':
            await bot.send_document(chat_id, (f'filtered_data.xlsx', filtered_data))
        else:
            await bot.send_message(chat_id, "There was an error generating the file.")


        if len(filters) == 1 and 'graph_theme' in filters:
            await post_filter_action_options(chat_id)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            start_over_button = types.KeyboardButton("🔄 Clear Filters")
            do_something_else_button = types.KeyboardButton("🔍 Keep Filters")
            markup.add(start_over_button, do_something_else_button)

            await bot.send_message(
                chat_id,
                "What would you like to do next?",
                reply_markup=markup
            )
    else:
        await bot.send_message(chat_id, "Invalid format choice. Please choose 'CSV' or 'Excel'.")

async def handle_check_graphs(message: types.Message):
    """Generate and send graphs based on the filtered data."""
    chat_id = message.chat.id
    filters = user_filters.get(chat_id, {})
    
    if not filters:
        await bot.send_message(chat_id, "⚠️ Please note that you have not applied any filters, so you will receive all information for all time.")
        filters = {} 
    
    theme = filters.get('graph_theme', 'dark')
    filtered_df, _ = add_filters_to_df(df, filters)
    
    if filtered_df.empty:
        await bot.send_message(chat_id, "Sorry, but we don't have data based on your filter. 🚫")
        await post_filter_action_options(chat_id)
    else :
        folder_path = f"figures/{chat_id}"
        os.makedirs(folder_path, exist_ok=True)

        await bot.send_message(chat_id, "✨ Generating graphs now! Please hold on for a moment (approximately 10 seconds)")
        generate_figures(filtered_df, chat_id, content_daily=False, light_theme=(theme == 'light'))
        
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        for txt in txt_files:
            try:
                with open(os.path.join(folder_path, txt), 'r', encoding='utf-8') as txt_file:
                    await bot.send_message(chat_id, txt_file.read())
            except Exception as e:
                print(f"Error sending text file {txt}: {e}")
    
        images = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        for image in images:
            try:
                with open(os.path.join(folder_path, image), 'rb') as img:
                    await bot.send_photo(chat_id, img)
            except Exception as e:
                print(f"Error sending image {image}: {e}")

        try:
            for file in os.listdir(folder_path):
                os.remove(os.path.join(folder_path, file))
            os.rmdir(folder_path)
        except Exception as e:
            print(f"Error deleting folder {folder_path}: {e}")

        if len(filters) == 1 and 'graph_theme' in filters:
            await post_filter_action_options(chat_id)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            start_over_button = types.KeyboardButton("🔄 Clear Filters")
            do_something_else_button = types.KeyboardButton("🔍 Keep Filters")
            markup.add(start_over_button, do_something_else_button)

            await bot.send_message(
                chat_id,
                "What would you like to do next?",
                reply_markup=markup
            )
            
        
async def handle_start_over(message: types.Message):
    """Handle the 'Start Over' button press."""
    chat_id = message.chat.id
    user_states[chat_id] = None
    
    await bot.send_message(chat_id, "Let's start over. Please select a filter option to begin:")
    await handle_filters(message) 


async def handle_do_something_else(message: types.Message):
    """Handle the 'Do Something Else with Filters' button press."""
    chat_id = message.chat.id
    user_states[chat_id] = WAITING_CURRENT_FILTERS 

    await post_filter_action_options(message.chat.id)


async def handle_another_date_selection(message: types.Message):
    """Send a message asking the user to input another date."""
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Back ⬅️"))
    await bot.send_message(chat_id, "Please provide another date in YYYY-MM-DD format", reply_markup=markup)
    user_states[chat_id] = WAITING_FOR_ANOTHER_DATE
    
    
async def handle_reset_daily_update_confirmation(message: types.Message):
    chat_id = message.chat.id
    if message.text == "Yes, delete the daily filter ✅":
        delete_user_data(chat_id)
        filters = user_filters.get(chat_id, {})
        if "notification_time" in filters:
            del filters["notification_time"]
        await bot.send_message(chat_id, "🔄 The daily update has been reset successfully! All filters have been cleared.")
        await send_start_message(chat_id, to_send_message=False)
        user_states[chat_id] = None
    elif message.text == "No, keep it ⬅️":
        await bot.send_message(chat_id, "The daily filter has been kept.")
        await send_start_message(chat_id, to_send_message=False)
        user_states[chat_id] = None
    else:
        await bot.send_message(chat_id, "Please choose a valid option.")
        
async def ask_to_change_theme(chat_id, current_theme, filters):
    """Ask the user if they want to change the graph theme."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    if current_theme == 'dark':
        theme_change_button = types.KeyboardButton("Light Theme 🌞")
    else:
        theme_change_button = types.KeyboardButton("Dark Theme 🌙")
    
    back_button = types.KeyboardButton("Back ⬅️")
    
    markup.add(theme_change_button, back_button)
    
    await bot.send_message(
        chat_id, 
        f"Your current theme is {'Dark' if current_theme == 'dark' else 'Light'}. Would you like to change it?",
        reply_markup=markup
    )
    user_states[chat_id] = WAITING_FOR_ANOTHER_THEME 
    
async def change_graph_theme(chat_id, new_theme, filters):
    """Change the graph theme and save it to the user's filters."""
    filters['graph_theme'] = new_theme
    user_filters[chat_id] = filters
    
    if new_theme == 'dark':
        await bot.send_message(chat_id, "Theme changed to Dark 🌙.")
    else:
        await bot.send_message(chat_id, "Theme changed to Light 🌞.")
        
    filters['graph_theme'] = new_theme
    await send_start_message(chat_id, to_send_message=False)
    user_states[chat_id] = None

async def handle_message(message: types.Message):
    """Handle incoming messages based on the user's current state."""
    chat_id = message.chat.id
    if message.text == "Back ⬅️":
        current_state = user_states.get(chat_id) 
        user_states.pop(chat_id, None)  
        
        if current_state in [WAITING_FOR_ANOTHER_DATE, WAITING_FOR_REVIEW, WAITING_FOR_ANOTHER_THEME, WAITING_FOR_FILTERS]:
            await send_start_message(message.chat.id, to_send_message=False)
        elif current_state in [WAITING_FOR_EXPERIENCE, WAITING_FOR_CORE_ROLE, WAITING_FOR_WORK_TYPE, WAITING_FOR_COMPANY,
                               WAITING_FOR_CITY, WAITING_FOR_REGION, WAITING_FOR_LANGUAGE,
                               WAITING_FOR_CITY_INPUT, WAITING_FOR_CORE_ROLE_INPUT, WAITING_FOR_COMPANY_INPUT,
                               WAITING_FOR_ACTION_AFTER_FILTER]:
            await handle_filters(message) 
        elif current_state in [WAITING_FOR_DATA_FORMAT, WAITING_FOR_NOTIFICATION_TIME,
                               WAITING_FOR_DAILY_UPDATE_CONFIRMATION,
                               WAITING_FOR_EMAIL]:
            await post_filter_action_options(message.chat.id)

    elif message.text == "Yesterday's Jobs":
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        filters = user_filters.get(chat_id, {})
        
        light_theme_filter = filters.get("graph_theme", "dark")
        file_suffix = f"{yesterday_date}-{light_theme_filter}"
        
        await check_and_post_files(chat_id, file_suffix)

    elif message.text == "Jobs by Date":
        await handle_another_date_selection(message)
        
    elif user_states.get(chat_id) in [WAITING_FOR_ANOTHER_DATE]:
            try:
                date_str = message.text
                datetime.strptime(date_str, '%Y-%m-%d')
                
                filters = user_filters.get(chat_id, {})
                light_theme_filter = filters.get("graph_theme", "dark")
                file_suffix = f"{date_str}-{light_theme_filter}"
                
                await check_and_post_files(chat_id, file_suffix)
            
            except ValueError:
                await bot.send_message(chat_id, "Invalid date format. Please provide the date in YYYY-MM-DD format or press 'Back ⬅️' to return.")

    elif message.text == "About Project":
        await send_project_info(chat_id)

    elif message.text == "Set Filters 🔍":
        await handle_filters(message)
        
    if user_states.get(chat_id) == WAITING_FOR_RATING:
        await handle_rating_submission(message)
    elif user_states.get(chat_id) == WAITING_FOR_REVIEW:
        await handle_review_submission(message)
    elif message.text == "Feedback ✍️":
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back_button = types.KeyboardButton("Back ⬅️")
        markup.add(back_button)

        await bot.send_message(chat_id, 
            "We'd love to hear your thoughts! 😊\nPlease share what you liked, what you didn't like, and any suggestions 💡 you have for improvements:",
            reply_markup=markup)
        
        user_states[chat_id] = WAITING_FOR_REVIEW
        
    elif message.text == "Change Graph Theme 🎨":
        chat_id = message.chat.id
        filters = user_filters.get(chat_id, {})
        current_theme = filters.get('graph_theme', 'dark')
        
        await ask_to_change_theme(chat_id, current_theme, filters)
        
    elif message.text == "Reset Daily Update ❌":
        chat_id = message.chat.id
        if user_exists(chat_id):
            filters = user_filters.get(chat_id, {})
            
            if filters:
                filters_info = ""
                for key, value in filters.items():
                    if key != "graph_theme" and key != "notification_time" and key != "email":
                        filters_info += f"{key.replace('_', ' ').capitalize()}: {value}\n"

                confirmation_msg = (
                    f"Your current filters are:\n{filters_info}\n"
                    "Are you sure you want to delete your daily filters?"
                )
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                yes_button = types.KeyboardButton("Yes, delete the daily filter ✅")
                no_button = types.KeyboardButton("No, keep it ⬅️")
                markup.add(yes_button, no_button)

                await bot.send_message(chat_id, confirmation_msg, reply_markup=markup)

                user_states[chat_id] = WAITING_RESET_DAILY_UPDATE
            else:
                await bot.send_message(chat_id, "You don't have any filters set.")
                await send_start_message(chat_id, to_send_message=False)
        else:
            await bot.send_message(chat_id, "You don't have any daily updates to reset.")
            await send_start_message(chat_id, to_send_message=False)

    elif user_states.get(chat_id) == WAITING_RESET_DAILY_UPDATE:
        await handle_reset_daily_update_confirmation(message)
    
    elif user_states.get(chat_id) == WAITING_FOR_DAILY_UPDATE_CONFIRMATION:
        filters = user_filters.get(chat_id, {})
        previous_time = filters.get("notification_time")

        buttons = [
            types.KeyboardButton("Back ⬅️"),
        ]

        if previous_time:
            buttons.append(types.KeyboardButton("Use Previous Time"))

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*buttons)

        if message.text == "Yes, apply for Daily Updates ✅":
            await bot.send_message(chat_id, f"When do you want to receive the daily update? Please provide the time in the format HH:MM (24-hour format). If you want to use your previous time {previous_time} please type 'Use Previous Time'", reply_markup=keyboard)
            user_states[chat_id] = WAITING_FOR_NOTIFICATION_TIME

        elif message.text == "Back ⬅️":
            await bot.send_message(chat_id, "Returning to the previous menu.")
            user_states[chat_id] = None
            await handle_filters(message)


    elif message.text == "Add Filter 🚀":
        await handle_filters(message) 
        return  
    
    elif message.text == "Clear Current Filters":
        await handle_clear_filters(chat_id) 
        
    elif message.text == "🔄 Clear Filters":
        current_filters = user_filters.get(chat_id, {})
        
        theme = current_filters.get('graph_theme', 'dark')
        notification_time = current_filters.get('notification_time', None)
        email = current_filters.get('email', None)
        
        user_filters[chat_id] = {
            'graph_theme': theme,
            'notification_time': notification_time,
            'email': email
        }
        
        await handle_start_over(message)

    elif message.text == "🔍 Keep Filters":
        await handle_do_something_else(message)
        
    elif user_states.get(chat_id) == WAITING_FOR_FILTERS:
        if message.text == "Experience Level 💼":
            await handle_experience_selection(message)
        elif message.text == "Role 🎯":
            await handle_core_role_selection(message)
        elif message.text == "Company 🏢":
            await handle_company_selection(message)
        elif message.text == "City 🌆":
            await handle_city_selection(message)
        elif message.text == "Region 🌍":
            await handle_region_selection(message)
        elif message.text == "Language 🗣️":
            await handle_language_selection(message)
        elif message.text == "Work Type 💻":
            await handle_work_type_selection(message)
        elif message.text == "Use Only Current Data 📅":
            chat_id = message.chat.id
            if chat_id not in user_filters:
                user_filters[chat_id] = {}
            user_filters[chat_id]['expiration_date'] = 'current'
            await bot.send_message(chat_id, "✅ You have selected to view only current job postings 📅. Expired listings will be excluded from your results 🗂️.")
            await post_filter_action_options(chat_id)
        elif message.text == "Use All Data 🔄":
            if chat_id in user_filters and 'expiration_date' in user_filters[chat_id]:
                del user_filters[chat_id]['expiration_date']
            await bot.send_message(chat_id, "✅ You have selected to view all data, including expired job postings 🔄.")
            await handle_filters(message)
        elif message.text == "Download Data ⬇️":
            await handle_download_filtered_data(message)
        elif message.text == "Check Graphs 📊":
            await handle_check_graphs(message)
        elif message.text == "Clear Filters 🗑️":
            chat_id = message.chat.id
            current_filters = user_filters.get(chat_id, {})
            
            theme = current_filters.get('graph_theme', 'dark')
            notification_time = current_filters.get('notification_time', None)
            email = current_filters.get('email', None)
            
            user_filters[chat_id] = {
                'graph_theme': theme,
                'notification_time': notification_time,
                'email': email
            }
            
            await bot.send_message(chat_id, "All filters have been cleared.")
            await handle_filters(message)
            
        elif message.text == "Apply for Daily Update 📅":
            await confirm_daily_update(message)
            
        elif message.text == "Current Filters 🔍":
            chat_id = message.chat.id
            filters = user_filters.get(chat_id, {})
            
            if filters:
                filters_msg = "\n".join([f"{key.replace('_', ' ').capitalize()}: {value}" 
                                        for key, value in filters.items() 
                                        if key != "graph_theme" and key != "notification_time" and key != "email"])
                if filters_msg: 
                    await bot.send_message(chat_id, f"Your current filters are:\n{filters_msg}")
                else:
                    await bot.send_message(chat_id, "You have not applied any filters yet.")
            else:
                await bot.send_message(chat_id, "You have not applied any filters yet.")
            
            await post_filter_action_options(chat_id)
            
    elif user_states.get(chat_id) == WAITING_FOR_EXPERIENCE:
        experience_level = message.text
        if experience_level in ["👶 Intern", "🌱 Junior", "🌿 Middle", "🌳 Senior", "🌟 Lead"]:
            current_value = user_filters.setdefault(chat_id, {}).get('experience_level', '')
            if current_value:
                user_filters[chat_id]['experience_level'] = f"{current_value};{experience_level}"
            else:
                user_filters[chat_id]['experience_level'] = experience_level
            await bot.send_message(chat_id, f"Added filter for experience level: {experience_level.capitalize()}")
            await post_filter_action_options(chat_id)
        else:
            await bot.send_message(chat_id, "Invalid experience level. Please choose one from the provided options.")

    elif user_states.get(chat_id) == WAITING_FOR_DATA_FORMAT:
        await handle_data_format_selection(message)
        
    elif user_states.get(chat_id) == WAITING_FOR_CORE_ROLE:
        core_role = message.text
        if core_role == "Other 🔄":
            await bot.send_message(chat_id, "Please type the core role you want to filter by:")
            user_states[chat_id] = WAITING_FOR_CORE_ROLE_INPUT
        else:
            if core_role in df['core_role'].values:
                current_value = user_filters.setdefault(chat_id, {}).get('core_role', '')
                if current_value:
                    user_filters[chat_id]['core_role'] = f"{current_value};{core_role}"
                else:
                    user_filters[chat_id]['core_role'] = core_role
                await bot.send_message(chat_id, f"Added filter for core role: {core_role.capitalize()}")
                await post_filter_action_options(chat_id)
            else:
                await bot.send_message(chat_id, "Invalid core role. Please type a valid core role from the dataset.")

    elif user_states.get(chat_id) == WAITING_FOR_CORE_ROLE_INPUT:
        core_role = message.text
        core_roles_list = df['core_role'].tolist()
        all_core_roles = set()
        
        for roles in core_roles_list:
            all_core_roles.update(roles.split(';'))
        
        if core_role in all_core_roles:
            current_value = user_filters.setdefault(chat_id, {}).get('core_role', '')
            if current_value:
                user_filters[chat_id]['core_role'] = f"{current_value};{core_role}"
            else:
                user_filters[chat_id]['core_role'] = core_role
            await bot.send_message(chat_id, f"Added filter for core role: {core_role}")
            await post_filter_action_options(chat_id)
        else:
            await check_column_and_suggest(message, 'core_role', WAITING_FOR_CORE_ROLE_INPUT)

    elif user_states.get(chat_id) == WAITING_FOR_WORK_TYPE:
        work_type = message.text
        if work_type in ['Full-time', 'Hybrid', 'Remote']:
            current_value = user_filters.setdefault(chat_id, {}).get('work_type', '')
            if current_value:
                user_filters[chat_id]['work_type'] = f"{current_value};{work_type}"
            else:
                user_filters[chat_id]['work_type'] = work_type
            await bot.send_message(chat_id, f"Added filter for work type: {work_type.capitalize()}")
            await post_filter_action_options(chat_id)
        else:
            await bot.send_message(chat_id, "Invalid work type. Please choose a value from the keyboard.")

    elif user_states.get(chat_id) == WAITING_FOR_COMPANY:
        company = message.text
        if company == "Other 🔄":
            await bot.send_message(chat_id, "Please type the company you want to filter by:")
            user_states[chat_id] = WAITING_FOR_COMPANY_INPUT
        else:
            if company in df['employer_name'].values:
                current_value = user_filters.setdefault(chat_id, {}).get('company', '')
                if current_value:
                    user_filters[chat_id]['company'] = f"{current_value};{company}"
                else:
                    user_filters[chat_id]['company'] = company
                await bot.send_message(chat_id, f"Added filter for company: {company.capitalize()}")
                await post_filter_action_options(chat_id)
            else:
                await bot.send_message(chat_id, "Invalid company. Please choose a valid company from the keyboard or select 'Other 🔄' to input manually.")

    elif user_states.get(chat_id) == WAITING_FOR_COMPANY_INPUT:
        company = message.text
        company_list = df['employer_name'].tolist()
        all_companies = set()
        for companies in company_list:
            all_companies.update(companies.split(';'))

        if company in all_companies:
            current_value = user_filters.setdefault(chat_id, {}).get('company', '')
            if current_value:
                user_filters[chat_id]['company'] = f"{current_value};{company}"
            else:
                user_filters[chat_id]['company'] = company
            await bot.send_message(chat_id, f"Added filter for company: {company}")
            await post_filter_action_options(chat_id)
        else:
            await check_column_and_suggest(message, 'employer_name', WAITING_FOR_COMPANY_INPUT)

    elif user_states.get(chat_id) == WAITING_FOR_CITY:
        city = message.text.strip().lower()  # Normalize user input
        if city == "other 🔄":
            await bot.send_message(chat_id, "Please type the city you want to filter by:")
            user_states[chat_id] = WAITING_FOR_CITY_INPUT
        else:
            normalized_cities = df['city'].str.split(';').explode().str.strip().str.lower()

            if city in normalized_cities.values:
                current_value = user_filters.setdefault(chat_id, {}).get('city', '')
                if current_value:
                    user_filters[chat_id]['city'] = f"{current_value};{city.capitalize()}"
                else:
                    user_filters[chat_id]['city'] = city.capitalize()
                
                await bot.send_message(chat_id, f"Added filter for city: {city.capitalize()}")
                await post_filter_action_options(chat_id)
            else:
                await bot.send_message(chat_id, "Invalid city. Please choose a valid city from the dataset or select 'Other 🔄' to input manually.")


    elif user_states.get(chat_id) == WAITING_FOR_CITY_INPUT:
        custom_city = message.text
        city_list = df['city'].tolist()
        all_cities = set()

        for cities in city_list:
            all_cities.update(cities.split(';'))

        if custom_city in all_cities:
            current_value = user_filters.setdefault(chat_id, {}).get('city', '')
            if current_value:
                user_filters[chat_id]['city'] = f"{current_value};{custom_city}"
            else:
                user_filters[chat_id]['city'] = custom_city
            await bot.send_message(chat_id, f"Added filter for city: {custom_city.capitalize()}")
            await post_filter_action_options(chat_id)
        else:
            await check_column_and_suggest(message, 'city', WAITING_FOR_CITY_INPUT)

    elif user_states.get(chat_id) == WAITING_FOR_REGION:
        region = message.text.strip().capitalize()  # Sanitize user input
        # Flatten the list of regions by splitting semicolon-separated entries
        regions = df['region'].unique()
        all_regions = set()

        for r in regions:
            split_regions = [region.strip() for region in r.split(';')]
            all_regions.update(split_regions)

        # Check if the region is valid
        if region in all_regions:
            current_value = user_filters.setdefault(chat_id, {}).get('region', '')
            if current_value:
                user_filters[chat_id]['region'] = f"{current_value};{region}"
            else:
                user_filters[chat_id]['region'] = region
            
            await bot.send_message(chat_id, f"Added filter for region: {region}")
            await post_filter_action_options(chat_id)
        else:
            regions_str = ', '.join(sorted(all_regions))  # Join all valid regions into a string
            await bot.send_message(chat_id, f"Sorry, we don't have data for this region right now. Here are all the regions we currently have: {regions_str}")
            
    elif user_states.get(chat_id) == WAITING_FOR_LANGUAGE:
        language = message.text
        if language in ["English 🇬🇧", "German 🇩🇪", "French 🇫🇷", "Spanish 🇪🇸", "Italian 🇮🇹", "Dutch 🇳🇱", \
                        "Russian 🇷🇺", "Mandarin 🇨🇳", "Japanese 🇯🇵", "Portuguese 🇵🇹", "Swedish 🇸🇪", "Danish 🇩🇰"]:
            current_value = user_filters.setdefault(chat_id, {}).get('language', '')
            if current_value:
                user_filters[chat_id]['language'] = f"{current_value};{language}"
            else:
                user_filters[chat_id]['language'] = language
            await bot.send_message(chat_id, f"Added filter for language: {language.capitalize()}")
            await post_filter_action_options(chat_id)
        else:
            await bot.send_message(chat_id, "Invalid language. Please choose a valid language from the dataset.")
            
    elif user_states.get(chat_id) == WAITING_FOR_NOTIFICATION_TIME:
        buttons = [
            types.KeyboardButton("Back ⬅️"),
            types.KeyboardButton("Skip 🚫"), 
        ]

        filters = user_filters.get(chat_id, {})
        previous_time = filters.get("notification_time")
        previous_email = filters.get("email")

        if message.text == "Use Previous Time":
            filters_json = json.dumps(filters)
            insert_user_data(chat_id, filters_json)

            await bot.send_message(chat_id, 
                f"⏰ Your daily update time has been set to {previous_time}!\n"
                "🔕 It might also be a good idea to mute this bot so you don't wake up too early! 😅"
            )

        else:
            try:
                preferred_time = datetime.strptime(message.text, "%H:%M").time()
                filters["notification_time"] = preferred_time.strftime("%H:%M")
                filters_json = json.dumps(filters)

                insert_user_data(chat_id, filters_json)

                await bot.send_message(chat_id, 
                    f"⏰ Your daily update time has been set to {preferred_time.strftime('%H:%M')}!\n"
                    "✅ Daily updates have been successfully applied!\n"
                    "🔕 It might also be a good idea to mute this bot so you don't wake up too early! 😅"
                )
            except ValueError:
                await bot.send_message(chat_id, "Invalid time format. Please provide the time in HH:MM format (24-hour format).")
                return

        def get_email_prompt(previous_email=None):
            if previous_email:
                return f"📧 Would you like to continue with your current email {previous_email} for receiving updates?"
            else:
                return "✉️ If you would like to receive updates via email, please enter your email in the format: youremail@gmail.com."

        if previous_email:
            buttons.append(types.KeyboardButton("Use Previous Email"))

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*buttons)

        email_prompt = get_email_prompt(previous_email)
        await bot.send_message(chat_id, email_prompt, reply_markup=keyboard)

        user_states[chat_id] = WAITING_FOR_EMAIL

            
    elif user_states.get(chat_id) == WAITING_FOR_EMAIL:
        if message.text == "Skip 🚫":
            await bot.send_message(chat_id, "You have opted to skip adding an email.")
            user_states[chat_id] = None
            await send_start_message(message.chat.id, to_send_message=False)
            
        def validate_email(email):
            email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
            return email_regex.match(email) is not None
        filters = user_filters.get(chat_id, {})
        previous_email = filters.get("email")

        
        if message.text == "Use Previous Email" and previous_email:
            filters["email"] = previous_email
            filters_json = json.dumps(filters)
            insert_user_data(chat_id, filters_json)

            await bot.send_message(chat_id, 
                f"📧 Your email has been set to {previous_email}!\n"
                "✅ You'll also receive your daily updates by email!"
            )
            user_states[chat_id] = None 
            await send_start_message(message.chat.id, to_send_message=False)

        elif message.text == "Back ⬅️":
            await bot.send_message(chat_id, "Returning to the previous menu.")
            user_states[chat_id] = WAITING_FOR_NOTIFICATION_TIME
            await handle_filters(message)

        elif validate_email(message.text.strip()):
            user_email = message.text.strip()
            filters["email"] = user_email
            filters_json = json.dumps(filters)
            insert_user_data(chat_id, filters_json)

            await bot.send_message(chat_id, "Great! You'll receive your updates by email as well.")
            user_states[chat_id] = None 
            await send_start_message(message.chat.id, to_send_message=False)

        else:
            await bot.send_message(chat_id, "Invalid email address. Please provide a valid email address.")
                
    elif message.text == "Light Theme 🌞":
        chat_id = message.chat.id
        filters = user_filters.get(chat_id, {})
        filters['graph_theme'] = 'light'
        await change_graph_theme(chat_id, 'light', filters)

    elif message.text == "Dark Theme 🌙":
        chat_id = message.chat.id
        filters = user_filters.get(chat_id, {})
        user_filters[chat_id] = filters
        await change_graph_theme(chat_id, 'dark', filters)
        

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """Handle /start command."""
    await send_start_message(message.chat.id, to_send_message=True)
    
async def send_message(user_id, text):
    """Send a message to a user."""
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        print(f"Failed to send message to {user_id}: {e}")
        
async def send_email(subject, body, to_email, excel_data, csv_data):
    from_email = 'makararena.pl@gmail.com'
    password = os.getenv("EMAIL_PASSWORD")

    if password is None:
        raise ValueError("EMAIL_PASSWORD environment variable not set")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    closing_message = f"\n\nSome day you'll find your dream job!\n 🌟 Have a nice day! 😊 \n\n"
    body += closing_message
    msg.attach(MIMEText(body, 'plain'))

    attachment_excel = MIMEApplication(excel_data)
    attachment_excel.add_header('Content-Disposition', 'attachment; filename="data.xlsx"')
    msg.attach(attachment_excel)

    attachment_csv = MIMEApplication(csv_data)
    attachment_csv.add_header('Content-Disposition', 'attachment; filename="data.csv"')
    msg.attach(attachment_csv)

    msg.attach(MIMEText("\nHere are both Excel and CSV data files attached.", 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        
async def check_and_send_notifications():
    while True:
        now = datetime.now().strftime('%H:%M')
        user_df = fetch_data(GET_FILTERS_QUERY)

        for _, row in user_df.iterrows():
            chat_id = row['user_id']
            filters = row['filters']
            chat_id = int(chat_id)

            if isinstance(filters, str):
                try:
                    filters_dict = json.loads(filters)
                except json.JSONDecodeError:
                    print(f"Failed to decode filters JSON for user_id {chat_id}")
                    continue
            elif isinstance(filters, dict):
                filters_dict = filters
            else:
                print(f"Unexpected type for filters for user_id {chat_id}")
                continue

            notification_time = filters_dict['notification_time']
            user_email = filters_dict.get('email')

            if notification_time == now:
                df_yesterday = fetch_data(YESTERDAY_JOBS_QUERY)
                message, excel_data, csv_data, _ = add_filters_to_df(df_yesterday, filters_dict, is_csv=False, is_excel=False, is_spark=True)
                
                if user_email:
                    subject = "Your Daily Update " + str(datetime.now().strftime('%Y-%m-%d'))
                    body = f"Here is your daily update for {datetime.now().strftime('%Y-%m-%d')}."

                try:
                    if message:
                        for part in message.split('\n'):
                            await send_message(chat_id, part)
                    
                    if excel_data and csv_data:
                        await bot.send_document(chat_id, ('data.xlsx', excel_data))
                        await bot.send_document(chat_id, ('data.csv', csv_data))

                        if user_email:
                            await send_email(subject, body, user_email, excel_data, csv_data)

                    closing_message = f"\nYour dream job awaits! 🌟 Have a nice day! 😊"
                    await bot.send_message(chat_id, closing_message)

                except Exception as e:
                    print(f"Failed to send message or file to user_id {chat_id}: {e}")
                    
        await asyncio.sleep(60)

async def on_startup(dp):
    """Initialize bot on startup and start the notification check loop."""
    asyncio.create_task(check_and_send_notifications())
    await load_all_user_data() 
    print("Bot startup completed and notification check loop started.")

@dp.message_handler()
async def handle_all_messages(message: types.Message):
    """Handle all other messages."""
    await handle_message(message)
    
def signal_handler(sig, frame):
    """Handle termination signals to save user data."""
    print("Signal received, saving user data and exiting...")
    for chat_id in user_states.keys():
        save_user_data_before_exit(chat_id, user_states[chat_id], user_filters.get(chat_id, {}))
    print("Exiting...")
    sys.exit(0)
    
    
def safe_json_loads(data):
    """Safely parse JSON data; return an empty dict if parsing fails or data is not a string."""
    if isinstance(data, str):
        try:
            return json.loads(data) if data else {}
        except json.JSONDecodeError:
            if len(data) > 5: 
                return data
            else :
                return {}

    elif isinstance(data, dict):
        return data
    else:
        return {}


def load_user_data():
    """Load all user data from the database into memory."""
    conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(conn_str)
    
    user_states = {}
    user_filters = {}

    try:
        query = LOAD_USER_DATA_QUERY
        with engine.connect() as conn:
            result = conn.execute(text(query))
            
            for row in result.fetchall():
                chat_id, state, filters = row
                user_states[chat_id] = safe_json_loads(state)
                user_filters[chat_id] = safe_json_loads(filters)
                print(f"Loaded data for user {chat_id} : {user_states[chat_id]} - {user_filters[chat_id]}")
                
    except Exception as e:
        print(f"Error loading user data from PostgreSQL database: {e}")
    
    return user_states, user_filters

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print("--------------------------------------\n Bot has started")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)