# 🇵🇱 IT Jobs Aggregator 🇵🇱

Welcome to my first big project, on which I have spent more than 2 months of my life. This is a Polish IT jobs aggregator, designed to help job seekers find their dream positions in the IT industry.

## Project Overview

This program starts with web scraping, accessing the three main IT job posting websites in Poland: pracuj.pl, buldogjob, and theprotocol.it. The program retrieves all the data about IT jobs posted daily. The entire job-scraping process takes about two hours.

After collecting the data, it is stored in two different databases:
1. **Historical Data Lake (Backup Table)**: Stores all raw data to ensure nothing is lost.
2. **Current Batch Table**: Stores data for preprocessing.

The data then undergoes an ETL (Extract, Transform, Load) or preprocessing step where it gets formatted and standardized. Insights are extracted from this data. The backup table is crucial in case something happens to the final preprocessed data, allowing for recovery of information from the last month.

After preprocessing, the data is saved to the main jobs table, which contains all jobs (expired and not expired) in a standardized format.

## Web Services

The project offers two web services:

1. **Dash App**: A local web application that you can access if you run the program on your own computer. (Website hosting is not currently available due to costs)

2. **Telegram Bot** : A detailed and convenient bot that allows you to:
   - Access all data through graphs
   - Download data in Excel or CSV format
   - Apply filters to the data (Experience Level , Role , City, Region, Language, Work Type)
   - Filter out only non-expired data or get all historical data
   - Change graphs to light or dark theme
   - Set daily alarms to receive information about new job postings matching your filters

3. **Automated Email Updates** : The program includes automatic email sending capabilities::
   - Email notifications about program execution and all preprocessing statuses are sent automatically to the main email.
   - Daily Update emails are sent to users, providing them with the latest job postings and relevant information.

## Project Potential

While the program may not be perfect and the code could be improved, the idea has great potential. This program can serve as a skeleton for new ideas in different areas. For example, it could be adapted to create a database of all flats in Poland (currently experiencing a boom). By rewriting the scrapers for relevant websites, changing database fields, and adjusting the filters, you could create a similar system for another sphere.

## Future Development

The current version of the program has room for improvement. Some algorithms could be optimized, and the bot has some bugs that need to be addressed. Due to time constraints (job searching and CS studies), major updates are not expected until next summer. However, this project has provided valuable experience in database handling, SQL, web scraping, and analytical Python tools like pandas, numpy, and dash.

## Project Schema

![Project Schema](./assets/ProjectSchema.png)

## How the App Works:

1. **Download Python 3.11.6**
   - For macOS:
     - Use Homebrew:
       ```bash
       brew install python@3.11.6
       ```
     - Or download from the official Python website and run the installer.
   - For Windows:
     - Download from the official Python website and run the installer.
   - For Linux:
     - Use your distribution's package manager, e.g., for Ubuntu:
       ```bash
       sudo apt-get update
       sudo apt-get install python3.11.6
       ```

2. **Clone this repository and navigate to the directory**
   ```bash
   git clone https://github.com/yourusername/work-analysis.git
   cd work-analysis
   ```

3. **Set up PostgreSQL with Docker**
   - Install Docker:
     - For macOS: Download Docker Desktop from the official Docker website.
     - For Windows: Download Docker Desktop from the official Docker website.
     - For Linux: Follow the official Docker installation guide for your distribution.

   - Pull the PostgreSQL Docker image:
     ```bash
     docker pull postgres
     ```

   - Create and run a PostgreSQL container:
     ```bash
     docker run --name work-analysis-db -e POSTGRES_PASSWORD=your_password -e POSTGRES_USER=your_user -e POSTGRES_DB=work_analysis -p 5432:5432 -d postgres
     ```

   - Verify that the container is running:
     ```bash
     docker ps
     ```

   - Access the PostgreSQL database (optional):
     ```bash
     docker exec -it work-analysis-db psql -U your_user -d work_analysis
     ```

4. **Create Tables in PostgreSQL**  
   Open your PostgreSQL instance and run the following SQL commands to create the necessary tables:

   ```sql
   -- This is the main table where all the preprocessed job data is stored
   CREATE TABLE public.jobs (
       id varchar(255) NOT NULL,
       job_title varchar(255) NULL,
       core_role varchar(255) NULL,
       employer_name varchar(255) NULL,
       city varchar(255) NULL,
       lat varchar(255) NULL,
       long varchar(255) NULL,
       region varchar(255) NULL,
       start_salary float8 NULL,
       max_salary float8 NULL,
       technologies_used text NULL,
       worker_responsibilities text NULL,
       job_requirements text NULL,
       offering text NULL,
       benefits text NULL,
       work_life_balance int4 NULL,
       financial_rewards_and_benefits int4 NULL,
       health_and_wellbeing int4 NULL,
       personal_and_professional_development int4 NULL,
       workplace_environment_and_culture int4 NULL,
       mobility_and_transport int4 NULL,
       unique_benefits int4 NULL,
       community_and_social_initiatives int4 NULL,
       b2b_contract int4 NULL,
       employment_contract int4 NULL,
       mandate_contract int4 NULL,
       substitution_agreement int4 NULL,
       work_contract int4 NULL,
       agency_agreement int4 NULL,
       temporary_staffing_agreement int4 NULL,
       specific_work_contract int4 NULL,
       internship_apprenticeship_contract int4 NULL,
       temporary_employment_contract int4 NULL,
       language_english int4 NULL,
       language_german int4 NULL,
       language_french int4 NULL,
       language_spanish int4 NULL,
       language_italian int4 NULL,
       language_dutch int4 NULL,
       language_russian int4 NULL,
       language_chinese_mandarin int4 NULL,
       language_japanese int4 NULL,
       language_portuguese int4 NULL,
       language_swedish int4 NULL,
       language_danish int4 NULL,
       internship int4 NULL,
       junior int4 NULL,
       middle int4 NULL,
       senior int4 NULL,
       "lead" int4 NULL,
       full_time int4 NULL,
       hybrid int4 NULL,
       remote int4 NULL,
       upload_id text NULL,
       expiration date NULL,
       url text NULL,
       date_posted date NULL,
       CONSTRAINT jobs_pkey PRIMARY KEY (id)
   );

   -- This table stores daily job data for processing. It is reset after each batch
   CREATE TABLE public.jobs_upload (
       id serial4 NOT NULL,
       job_title varchar NULL,
       employer_name varchar NULL,
       "location" varchar NULL,
       hybryd_full_remote varchar NULL,
       expiration varchar NULL,
       contract_type varchar NULL,
       experience_level varchar NULL,
       salary varchar NULL,
       technologies text NULL,
       responsibilities text NULL,
       requirements text NULL,
       offering text NULL,
       benefits text NULL,
       url varchar NULL,
       date_posted timestamp NULL,
       upload_id varchar NULL,
       CONSTRAINT jobs_upload_pkey PRIMARY KEY (id)
   );

   -- This is the backup table. It stores job data to revert to a previous state if needed
   CREATE TABLE public.jobs_upload_backup (
       id serial4 NOT NULL,
       job_title varchar NULL,
       employer_name varchar NULL,
       "location" varchar NULL,
       hybryd_full_remote varchar NULL,
       expiration varchar NULL,
       contract_type varchar NULL,
       experience_level varchar NULL,
       salary varchar NULL,
       technologies text NULL,
       responsibilities text NULL,
       requirements text NULL,
       offering text NULL,
       benefits text NULL,
       url varchar NULL,
       date_posted timestamp NULL,
       upload_id varchar NULL,
       CONSTRAINT jobs_upload_backup_pkey PRIMARY KEY (id)
   );

   -- This table stores user filters for sending daily updates
   CREATE TABLE public.user_data (
       user_id int8 NOT NULL,
       filters jsonb NULL,
       CONSTRAINT user_data_pkey PRIMARY KEY (user_id)
   );

   -- This table stores user data to preserve bot state before exit and restore it later
   CREATE TABLE public.user_data_before_exit (
       chat_id int8 NOT NULL,
       state jsonb NULL,
       filters jsonb NULL,
       CONSTRAINT user_data_before_exit_pkey PRIMARY KEY (chat_id)
   );

   -- This table stores user reviews
   CREATE TABLE public.user_reviews (
       id serial4 NOT NULL,
       chat_id int8 NOT NULL,
       username varchar(50) NULL,
       user_name varchar(100) NULL,
       review text NULL,
       rating int4 NULL,
       review_type varchar(50) NULL,
       chat_type varchar(50) NULL,
       created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
       CONSTRAINT user_reviews_pkey PRIMARY KEY (id),
       CONSTRAINT user_reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
   );

   -- This table is for storing daily report figures
  CREATE TABLE daily_report (
      generation_id VARCHAR(50) PRIMARY KEY,
      benefits_pie_chart BYTEA,
      city_bubbles_chart BYTEA,
      city_pie_chart BYTEA,
      employer_bar_chart BYTEA,
      employment_type_pie_chart BYTEA,
      experience_level_bar_chart BYTEA,
      languages_bar_chart BYTEA,
      salary_box_plot BYTEA,
      poland_map BYTEA,
      positions_bar_chart BYTEA,
      technologies_bar_chart BYTEA,
      summary TEXT
  );
   ```
   
5. **Add execute permissions to scripts (macOS and Linux only)**
   - For macOS and Linux:
     ```bash
     chmod +x main.sh
     chmod +x control_bot.sh
     ```

6. **Create .env file**
   - Create a file named `.env` in the root directory of the project with the following content:
     ```plaintext
     TELEGRAM_TOKEN=your_telegram_bot_token
     DB_PASSWORD=your_database_password
     EMAIL_PASSWORD=your_email_password
     ```

7. **Run the script**
   - For macOS and Linux:
     ```bash
     ./main.sh
     ```
   - For Windows:
     Create a batch file named `main.bat` with the following content:
     ```batch
     @echo off
     python main.py
     ```
     Then run it:
     ```
     main.bat
     ```

8. **Set up automated script execution**
   - For macOS and Linux:
     Run `crontab -e` and add the following line:
     ```
     00 5 * * * /path/to/your/main.sh >> /path/to/your/logs.log 2>&1
     ```
   - For Windows:
     Use Task Scheduler:
     1. Open Task Scheduler
     2. Create a new task
     3. Set the trigger to run daily at 5:00 AM
     4. Set the action to start a program: `C:\Windows\System32\cmd.exe`
     5. Add arguments: `/c C:\path\to\your\main.bat >> C:\path\to\your\logs.log 2>&1`

Remember to replace `/path/to/your/` or `C:\path\to\your\` with the actual path to your script and log file.

This setup will allow you to run the Work-Analysis project on macOS, Windows, and Linux systems, with automated daily execution.