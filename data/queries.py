# Queries for daily reports
INSERT_DAILY_REPORT_QUERY = """
    INSERT INTO daily_report (
        generation_id, 
        benefits_pie_chart, 
        city_bubbles_chart, 
        city_pie_chart, 
        employer_bar_chart, 
        employment_type_pie_chart, 
        experience_level_bar_chart, 
        languages_bar_chart, 
        salary_box_plot, 
        poland_map, 
        positions_bar_chart, 
        technologies_bar_chart, 
        summary
    ) VALUES (
        :generation_id, 
        :benefits_pie_chart, 
        :city_bubbles_chart, 
        :city_pie_chart, 
        :employer_bar_chart, 
        :employment_type_pie_chart, 
        :experience_level_bar_chart, 
        :languages_bar_chart, 
        :salary_box_plot, 
        :poland_map, 
        :positions_bar_chart, 
        :technologies_bar_chart, 
        :summary
    )
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
        summary = EXCLUDED.summary;
"""

# Queries for user data
INSERT_USER_DATA_QUERY = """
    INSERT INTO user_data (user_id, filters)
    VALUES (:user_id, :filters)
    ON CONFLICT (user_id) 
    DO UPDATE SET filters = EXCLUDED.filters;
"""

DELETE_USER_DATA_QUERY = """
    DELETE FROM user_data 
    WHERE user_id = :user_id;
"""

CHECK_IF_USER_EXIST_QUERY = """
    SELECT 1 
    FROM user_data 
    WHERE user_id = :user_id;
"""

# Queries for user data before exit
INSERT_USER_DATA_BEFORE_EXIT_QUERY = """
    INSERT INTO user_data_before_exit (chat_id, state, filters)
    VALUES (:chat_id, :state, :filters)
    ON CONFLICT (chat_id) 
    DO UPDATE SET state = EXCLUDED.state, filters = EXCLUDED.filters;
"""

LOAD_USER_DATA_QUERY = """
    SELECT chat_id, state, filters 
    FROM user_data_before_exit;
"""

# Queries for jobs
ALL_JOBS_QUERY = """
    SELECT * 
    FROM jobs;
"""

ALL_FROM_JOBS_UPLOAD_QUERY = """
    SELECT * 
    FROM jobs_upload;
"""

UNIQUE_JOBS_QUERY = """
    SELECT id, technologies_used 
    FROM jobs;
"""

YESTERDAY_JOBS_QUERY = """
    SELECT * 
    FROM jobs 
    WHERE date_posted = CURRENT_DATE - INTERVAL '1 day';
"""

GET_FILTERS_QUERY = """
    SELECT user_id, filters 
    FROM user_data;
"""

# Queries for plots and reports
LOAD_ALL_PLOTS_QUERY = """
    SELECT 
        benefits_pie_chart, 
        city_bubbles_chart, 
        city_pie_chart, 
        employer_bar_chart, 
        employment_type_pie_chart, 
        experience_level_bar_chart, 
        languages_bar_chart, 
        salary_box_plot, 
        poland_map, 
        positions_bar_chart, 
        technologies_bar_chart, 
        summary
    FROM daily_report
    WHERE generation_id = :date_str;
"""

GET_CLOSEST_DATE_QUERY = """
    SELECT generation_id
    FROM daily_report
    WHERE generation_id != :date_str
    ORDER BY generation_id DESC
    LIMIT 1;
"""

# Queries for user reviews
INSERT_USER_REVIEW_QUERY = """
    INSERT INTO user_reviews (chat_id, username, user_name, review, rating, review_type, chat_type)
    VALUES (:chat_id, :username, :user_name, :review, :rating, :review_type, :chat_type);
"""