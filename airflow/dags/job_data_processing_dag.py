from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import os
import subprocess
import signal
from datetime import datetime

PROJECT_DIR = "/Users/ivanivsnov/dev/Polish-IT-Jobs-Aggregator"
EMAIL = "makararena@gmail.com"
TODAYS_DATE = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
PID_FILE = os.path.join(PROJECT_DIR, 'logs', 'bot.pid')
LOG_DIR = os.path.join(PROJECT_DIR, 'logs')
MAIN_LOG_FILE = os.path.join(LOG_DIR, 'main.log')
BOT_LOG_FILE = os.path.join(LOG_DIR, 'bot.log')

def clear_logs():
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(MAIN_LOG_FILE, 'w') as main_log, open(BOT_LOG_FILE, 'w') as bot_log:
        main_log.write("Log files cleared at {}\n".format(datetime.now()))
        bot_log.write("Bot log initialized at {}\n".format(datetime.now()))
    if os.path.exists(os.path.join(LOG_DIR, 'logs.zip')):
        os.remove(os.path.join(LOG_DIR, 'logs.zip'))

def setup_environment():
    venv_path = os.path.join(PROJECT_DIR, 'venv')
    if not os.path.exists(venv_path):
        subprocess.run(['python', '-m', 'venv', venv_path], check=True)
    activate_command = f"source {venv_path}/bin/activate && pip install --upgrade pip && pip install -r {os.path.join(PROJECT_DIR, 'requirements.txt')}"
    subprocess.run(activate_command, shell=True, executable='/bin/bash', check=True)

def run_scrapy_spiders():
    spiders_dir = os.path.join(PROJECT_DIR, 'workscrapper', 'workscrapper')
    if os.path.isdir(spiders_dir):
        os.chdir(spiders_dir)
        subprocess.run(['scrapy', 'crawl', 'pracuj_pl_spider'], stdout=open(MAIN_LOG_FILE, 'a'), stderr=subprocess.STDOUT)
    else:
        raise FileNotFoundError(f"Directory {spiders_dir} not found.")

def run_preprocessing():
    subprocess.run(['venv/bin/python', 'job_data_processing.py'], stdout=open(MAIN_LOG_FILE, 'a'), stderr=subprocess.STDOUT)

def send_email_with_logs():
    subprocess.run(['venv/bin/python', 'email_sender.py',
                    '--subject', f"Daily Preprocess Logs and Status - {TODAYS_DATE}",
                    '--body', "Preprocess logs attached.",
                    '--to', EMAIL,
                    '--attachment', MAIN_LOG_FILE], check=True)

def log_message(message):
    with open(MAIN_LOG_FILE, 'a') as log_file:
        log_file.write(f"{message} at {datetime.now()}\n")

with DAG(
    dag_id='project_setup_dag',
    schedule_interval='*/3 * * * *',
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=2,
    default_args={'depends_on_past': False}
) as dag:

    clear_logs_task = PythonOperator(
        task_id='clear_logs',
        python_callable=clear_logs,
    )

    setup_task = PythonOperator(
        task_id='setup_environment',
        python_callable=setup_environment,
    )

    run_spiders_task = PythonOperator(
        task_id='run_scrapy_spiders',
        python_callable=run_scrapy_spiders,
    )

    run_preprocess_task = PythonOperator(
        task_id='run_preprocessing',
        python_callable=run_preprocessing,
    )

    send_email_task = PythonOperator(
        task_id='send_email_with_logs',
        python_callable=send_email_with_logs,
    )

    clear_logs_task >> setup_task >> run_spiders_task >> run_preprocess_task >> send_email_task
