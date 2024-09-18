from sqlalchemy import text

# Queries for daily reports
INSERT_DAILY_REPORT_QUERY = text("""
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
        technologies_bar_chart, x
        responsibilities_wordcloud,   
        requirements_wordcloud,       
        offering_wordcloud,           
        benefits_wordcloud,          
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
        :responsibilities_wordcloud,   
        :requirements_wordcloud,    
        :offering_wordcloud,         
        :benefits_wordcloud,          
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
        responsibilities_wordcloud = EXCLUDED.responsibilities_wordcloud,  
        requirements_wordcloud = EXCLUDED.requirements_wordcloud,      
        offering_wordcloud = EXCLUDED.offering_wordcloud,             
        benefits_wordcloud = EXCLUDED.benefits_wordcloud,               
        summary = EXCLUDED.summary
""")


# Queries for user data before exit
INSERT_USER_DATA_BEFORE_EXIT_QUERY = text("""
    INSERT INTO user_data_before_exit (chat_id, state, filters, filters_for_notification)
    VALUES (:chat_id, :state, :filters, :filters_for_notification)
    ON CONFLICT (chat_id) 
    DO UPDATE SET 
        state = EXCLUDED.state, 
        filters = EXCLUDED.filters,
        filters_for_notification = EXCLUDED.filters_for_notification;
""")

LOAD_USER_DATA_QUERY = text("""
    SELECT chat_id, state, filters, filters_for_notification
    FROM user_data_before_exit;
""")

# Queries for jobs
ALL_JOBS_QUERY = text("""
    SELECT * 
    FROM jobs;
""")

ALL_FROM_JOBS_UPLOAD_QUERY = text("""
    SELECT * 
    FROM jobs_upload;
""")

UNIQUE_JOBS_QUERY = text("""
    SELECT id, technologies_used 
    FROM jobs;
""")

YESTERDAY_JOBS_QUERY = text("""
    SELECT * 
    FROM jobs 
    WHERE date_posted = CURRENT_DATE - INTERVAL '1 day';
""")

# Queries for plots and reports
LOAD_ALL_PLOTS_QUERY = text("""
    SELECT *
    FROM daily_report
    WHERE generation_id = :date_str;
""")

GET_CLOSEST_DATE_QUERY = text("""
    SELECT generation_id
    FROM daily_report
    WHERE generation_id != :date_str
    ORDER BY generation_id DESC
    LIMIT 1;
""")

# Queries for user reviews
INSERT_USER_REVIEW_QUERY = text("""
    INSERT INTO user_reviews (chat_id, username, user_name, review, rating, review_type, chat_type)
    VALUES (:chat_id, :username, :user_name, :review, :rating, :review_type, :chat_type);
""")