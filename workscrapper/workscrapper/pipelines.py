import psycopg2
import os
import json
from dotenv import load_dotenv
load_dotenv()

class PostgreSQLPipeline:
    def open_spider(self, spider):
        db_config = json.loads(os.getenv('DB_CONFIG'))
        
        self.connection = psycopg2.connect(
            dbname=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host']
        )
        self.cursor = self.connection.cursor()

        if spider.name == "pracuj_pl_spider":
            try:
                self.cursor.execute("""
                    DROP TABLE IF EXISTS jobs_upload;
                """)
                self.cursor.execute("""
                    CREATE TABLE jobs_upload (
                        id SERIAL PRIMARY KEY,
                        job_title VARCHAR,
                        employer_name VARCHAR,
                        location VARCHAR,
                        hybryd_full_remote VARCHAR,
                        expiration VARCHAR,
                        contract_type VARCHAR,
                        experience_level VARCHAR,
                        salary VARCHAR,
                        technologies TEXT,
                        responsibilities TEXT,
                        requirements TEXT,
                        offering TEXT,
                        benefits TEXT,
                        url VARCHAR,
                        date_posted TIMESTAMP,
                        upload_id VARCHAR
                    );
                """)

                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs_upload_backup (
                        id SERIAL PRIMARY KEY,
                        job_title VARCHAR,
                        employer_name VARCHAR,
                        location VARCHAR,
                        hybryd_full_remote VARCHAR,
                        expiration VARCHAR,
                        contract_type VARCHAR,
                        experience_level VARCHAR,
                        salary VARCHAR,
                        technologies TEXT,
                        responsibilities TEXT,
                        requirements TEXT,
                        offering TEXT,
                        benefits TEXT,
                        url VARCHAR,
                        date_posted TIMESTAMP,
                        upload_id VARCHAR
                    );
                """)

                self.connection.commit()
            except Exception as e:
                print(f"Error setting up the database table: {e}")
                self.connection.rollback()

    def close_spider(self, spider):
        try:
            self.connection.commit()
        except Exception as e:
            print(f"Error committing transaction: {e}")
        finally:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()

    # Add 'spider' argument here
    def process_item(self, item, spider):
        try:
            # Insert into the main table
            self.cursor.execute("""
                INSERT INTO jobs_upload (
                    job_title, employer_name, location, hybryd_full_remote, expiration, contract_type,
                    experience_level, salary, technologies, responsibilities, requirements,
                    offering, benefits, url, date_posted, upload_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get('job_title'),
                item.get('employer_name'),
                item.get('location'),
                item.get('hybryd_full_remote'),
                item.get('expiration'),
                item.get('contract_type'),
                item.get('experience_level'),
                item.get('salary'),
                item.get('technologies'),
                item.get('responsibilities'),
                item.get('requirements'),
                item.get('offering'),
                item.get('benefits'),
                item.get('url'),
                item.get('date_posted'),
                item.get('upload_id')
            ))

            # Insert into the backup table
            self.cursor.execute("""
                INSERT INTO jobs_upload_backup (
                    job_title, employer_name, location, hybryd_full_remote, expiration, contract_type,
                    experience_level, salary, technologies, responsibilities, requirements,
                    offering, benefits, url, date_posted, upload_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get('job_title'),
                item.get('employer_name'),
                item.get('location'),
                item.get('hybryd_full_remote'),
                item.get('expiration'),
                item.get('contract_type'),
                item.get('experience_level'),
                item.get('salary'),
                item.get('technologies'),
                item.get('responsibilities'),
                item.get('requirements'),
                item.get('offering'),
                item.get('benefits'),
                item.get('url'),
                item.get('date_posted'),
                item.get('upload_id')
            ))

            self.connection.commit()

        except Exception as e:
            print(f"Error inserting item: {e}")
            self.connection.rollback()

        return item