CONTRACT_VALUES = {
    'contract of employment': 'Contract of Employment',
    'umowa o pracę': 'Contract of Employment',
    'kontrakt B2B': 'B2B Contract',
    'contract of employment (full-time)': 'Contract of Employment (Full-Time)',
    'umowa o pracę (pełny etat)': 'Contract of Employment (Full-Time)',
    'kontrakt B2B (pełny etat)': 'B2B Contract (Full-Time)',
    'umowa o pracę, kontrakt B2B': 'Contract of Employment, B2B Contract',
    'contract of employment, B2B contract': 'Contract of Employment, B2B Contract',
    'umowa o pracę, kontrakt B2B (pełny etat)': 'Contract of Employment, B2B Contract (Full-Time)',
    'umowa o pracę, umowa na zastępstwo': 'Contract of Employment, Substitution Agreement',
    'contract of employment, B2B contract (full-time)': 'Contract of Employment, B2B Contract (Full-Time)',
    'umowa o pracę, umowa zlecenie, kontrakt B2B': 'Contract of Employment, Contract of Mandate, B2B Contract',
    'other': 'Other',
    'Other': 'Other',
    'B2B contract': 'B2B Contract',
    'B2B contract (full-time)': 'B2B Contract (Full-Time)',
    'contract of mandate': 'Contract of Mandate',
    'substitution agreement': 'Substitution Agreement',
    'contract of work': 'Contract of Work',
    'agency agreement': 'Agency Agreement',
    'temporary staffing agreement': 'Temporary Staffing Agreement',
    'contract for specific work': 'Contract for Specific Work',
    'internship, apprenticeship contract': 'Internship, Apprenticeship Contract',
    'contract of temporary employment': 'Contract of Temporary Employment',
    'kontrakt B2B, umowa o pracę': 'Contract of Employment, B2B Contract',
    'kontrakt B2B, umowa o pracę to this B2B Contract': 'Contract of Employment, B2B Contract',
    'umowa zlecenie': 'Contract of Mandate',
    'umowa zlecenie (pełny etat)': 'Contract of Mandate (Full-Time)',
    'umowa o dzieło, umowa zlecenie, kontrakt B2B': 'Contract of Work, Contract of Mandate, B2B Contract',
    'umowa zlecenie, kontrakt B2B': 'Contract of Mandate, B2B Contract',
    'umowa o pracę (część etatu, pełny etat)': 'Contract of Employment (Part-Time, Full-Time)',
    'contract of employment (full-time, part time)': 'Contract of Employment (Full-Time, Part-Time)',
    'Employment contract': 'Contract of Employment',
}

POLISH_TO_ENGLISH_MONTH = {
        'stycznia': 'January', 'lutego': 'February', 'marca': 'March', 'kwietnia': 'April',
        'maja': 'May', 'czerwca': 'June', 'lipca': 'July', 'sierpnia': 'August',
        'września': 'September', 'października': 'October', 'listopada': 'November', 'grudnia': 'December',
        "lispada" : "November "
    }

CATEGORIES_BENEFITS = {
    'work_life_balance': [
        'volunteering', 'remote work', 'days off', 'workday', 'day off', 'work-life', 'home office',
        'work remotely', 'Flexible working hours', 'Volunteer hours', 'possibility of remote work', 
        'one shorter workday', 'time for development of your ideas', 'additional leave', 
        '+3 days off for fathers due to the birth of a child', 'remote work opportunities', 
        'flexible work from home scheme after pandemic/lockdown', 'flexible working time', 
        'Remote/hybrid work', 'Freedom to choose your working model (HO/hybrid/office)', 'extra leave', 
        'additional days off for parents'
    ],
    'financial_rewards_and_benefits': [
        'salary', 'compensation', 'bonus', 'holiday funds', 'cafeteria platform', 'bonus system', 
        'redeployment package', 'social fund', 'life insurance', 'preferential loans', 'Beer allowance', 
        'discounts on equipment purchases in our stores', 'child’s starter kit', 'MultiSport card', 
        'summer and winter activities for children', 'Christmas bonuses', 'Christmas packages', 
        'equity', 'MBA support', 'IP tax benefit', 'Financial bonus', 'Copyright Tax Deduction', 
        'development budget', 'Christmas bonus', 'Money for moving expenses'
    ],
    'health_and_wellbeing': [
        'medical', 'care', 'health', 'wellbeing', 'psychological support', 'medical care', 'mental health', 
        'Healthcare package', 'Life insurance', 'dental care', 'wellbeing program', 'massage services at the office', 
        'mentoring care', 'funding for private medical care Medicover', 'Leisure package for families', 
        'Healthcare package for families', 'gym access', 'massage services', 'Yoga', 'sports teams', 'cycling club', 
        'wellbeing initiatives', 'health screenings', 'vaccination programs', 'ergonomic office setup'
    ],
    'personal_and_professional_development': [
        'training', 'course', 'certification', 'development', 'academy', 'learning', 'Mentoring and coaching', 
        'funding for training and courses', 'external training', 'foreign language lessons', 
        'Employee psychological support program', 'soft skills training', 'access to +100 projects', 
        'employee referral program', 'workshops and webinars for employees', 'technical support from technology leaders', 
        'MBA support', 'development budget', 'conferences in Poland', 'conferences abroad', 
        'access to e-learning platforms', 'access to Pluralsight'
    ],
    'workplace_environment_and_culture': [
        'office', 'workspace', 'environment', 'modern office', 'office equipment', 'Non-corporate atmosphere', 
        'Chill room', 'physiotherapy sessions in the company', 'video games at work', 'Relaxation room', 'Game room', 
        'space for experimenting', 'electric vehicle charging stations', 'modern & ergonomic eco-office', 
        'convenient location (WIERZBNO)', 'Playground and grill', 'in-house gym', 'modern ergonomic office', 
        'casual dress code', 'gaming room', 'library', 'fruit days', 'free snacks', 'hot beverages', 'fruits', 
        'coffee', 'tea', 'cold beverages', 'baby layette', 'family-friendly initiatives', 'holiday events', 
        'birthday celebrations', 'Integration events', 'Innovation Days', 'open bar on Fridays'
    ],
    'mobility_and_transport': [
        'car leasing', 'parking', 'bike parking', 'employee parking', 'Help finding an apartment', 'prime mobility', 
        'Visa Services', 'temporary housing', 'electric vehicle charging stations', 'shower facilities', 
        'subsidized commuting costs'
    ],
    'unique_benefits': [
        'Beer allowance', 'company supports open source projects', 'unlimited free access to Copernicus Science Center', 
        'Prime Academy', 'Open to Ukrainian candidates', 'employee discounts', 'deputat beer', 
        'saving & investment scheme'
    ],
    'community_and_social_initiatives': [
        'volunteering opportunities', 'charity initiatives', 'help in finding an apartment', 'family picnics', 
        'Integration events', 'company library', 'cultural events', 'workshops & webinars for employees', 
        'conferences abroad', 'conferences in Poland', 'company sports teams', 'cycling club', 'picnics', 
        'social impact initiatives', 'diversity and inclusion programs'
    ]
}

LANGUAGES = {
    "English": ["English", "Angielski", "Angielsku"],
    "German": ["German", "Deutsch", "Niemiecki", "Niemiecku"],
    "French": ["French", "Français", "Francuski", "Francusku"],
    "Spanish": ["Spanish", "Español", "Hiszpański", "Hiszpańsku"],
    "Italian": ["Italian", "Italiano", "Włoski", "Włosku"],
    "Dutch": ["Dutch", "Nederlands", "Holenderski", "Holendersku"],
    "Russian": ["Russian", "Русский", "Rosyjski", "Rosyjsku"],
    "Mandarin": ["Mandarin", "普通话", "Mandaryński", "Mandaryńsku"],
    "Japanese": ["Japanese", "日本語", "Japoński", "Japońsku"],
    "Portuguese": ["Portuguese", "Português", "Portugalski", "Portugalsku"],
    "Swedish": ["Swedish", "Svenska", "Szwedzki", "Szwedzku"],
    "Danish": ["Danish", "Dansk", "Duński", "Duńsku"]
}

LANGUAGES_BOT = [
    "English",
    "German",
    "French",
    "Spanish",
    "Italian",
    "Dutch",
    "Russian",
    "Mandarin",
    "Japanese",
    "Portuguese",
    "Swedish",
    "Danish"
]

JOB_LEVEL_DICT = {
    'specialist (Mid / Regular)': 'middle','junior specialist (Junior)': 'junior',
    'specjalista (Mid / Regular)': 'middle','senior specialist (Senior), expert': 'lead',
    'senior specialist (Senior)': 'senior','menedżer': 'senior',
    'starszy specjalista (Senior)': 'senior','praktykant / stażysta': 'internship','team manager': 'lead',
    'trainee': 'internship','specjalista (Mid / Regular), starszy specjalista (Senior)': 'senior',
    'specialist (Mid / Regular), senior specialist (Senior)': 'senior','starszy specjalista (Senior), ekspert': 'lead','asystent, młodszy specjalista (Junior)': 'junior',
    'asystent': 'junior','{expert}': 'lead','kierownik / koordynator': 'lead','specjalista (Mid / Regular), młodszy specjalista (Junior)': 'middle',
    'młodszy specjalista (Junior)': 'junior','{mid}': 'middle','{senior}': 'senior','{manager}': 'senior',
    '{lead}': 'lead','junior': 'junior','senior ekspert': 'lead','mid / regular': 'middle','senior expert': 'lead',
    'senior specialist': 'senior','manager / supervisor': 'lead','Mid/Regular': 'middle',
    'Junior': 'junior','Senior': 'senior','Internship': 'internship','Lead': 'lead',
    'specjalista (Mid / Regular), junior specialist (Junior)': 'middle',
    'młodszy specjalista (Junior)': 'junior','specjalista': 'middle','dyrektor': 'lead',
    'senior manager': 'lead','head manager': 'lead','starszy specjalista (Lead)': 'lead',
    'specialist (Mid / Regular), junior specialist (Junior)': 'middle','{"senior • expert"}': 'senior',
    '{"junior • mid"}': 'middle','{"mid • senior"}': 'senior','{junior}': 'junior','{"lead • manager"}': 'lead'
}

DICT_TO_RENAME = {'technologies':'technologies_used','responsibilities':'worker_responsibilities',
        'requirements':'job_requirements','B2B Contract':'b2b_contract','Contract of Employment': 'employment_contract',
        'Contract of Mandate': 'mandate_contract','Substitution Agreement': 'substitution_agreement',
        'Contract of Work': 'work_contract','Agency Agreement': 'agency_agreement',
        'Temporary Staffing Agreement': 'temporary_staffing_agreement','Contract for Specific Work': 'specific_work_contract',
        'Internship / Apprenticeship Contract': 'internship_apprenticeship_contract',
        'Contract of Temporary Employment': 'temporary_employment_contract',
        'Backend': 'backend',
        'Frontend': 'frontend',
        'Full-stack': 'full_stack',
        'Mobile': 'mobile',
        'Architecture': 'architecture',
        'DevOps': 'devops',
        'Game dev': 'game_dev',
        'Big Data / Data Science': 'big_data_data_science',
        'Embedded': 'embedded',
        'QA/Testing': 'qa_testing',
        'Security': 'security',
        'Helpdesk': 'helpdesk',
        'Product Management': 'product_management',
        'Project Management': 'project_management',
        'Agile': 'agile',
        'UX/UI': 'ux_ui',
        'Business analytics': 'business_analytics',
        'System analytics': 'system_analytics',
        'SAP&ERP': 'sap_erp',
        'IT admin': 'it_admin',
        'AI/ML': 'ai_ml',
        'English': 'language_english',
        'German': 'language_german',
        'French': 'language_french',
        'Spanish': 'language_spanish',
        'Italian': 'language_italian',
        'Dutch': 'language_dutch',
        'Russian': 'language_russian',
        'Mandarin': 'language_chinese_mandarin',
        'Japanese': 'language_japanese',
        'Portuguese': 'language_portuguese',
        'Swedish': 'language_swedish',
        'Danish': 'language_danish',
        'Internship': 'internship',
        'Entry level': 'entry_level',
        'Mid-Senior level': 'mid_senior_level',
        'Director': 'director'}

WORK_TYPE_DICT = {
    'full_time': ['full office work', 'Full Time', 'praca stacjonarna', 'home office work'],
    'hybrid': ['remote work', 'praca hybrydowa', 'hybrid work', 'praca hybrydowa'],
    'remote': ['praca zdalna', 'Remote', 'hybrid work', 'praca mobilna']
}


COLUMNS_ORDER = [
    "id", "job_title", "core_role", "employer_name", "city", "lat", "long", 
    "region", "start_salary", "max_salary", "technologies_used", 
    "worker_responsibilities", "job_requirements", "offering", "benefits", 
    "work_life_balance", "financial_rewards_and_benefits", 
    "health_and_wellbeing", "personal_and_professional_development", 
    "workplace_environment_and_culture", "mobility_and_transport", 
    "unique_benefits", "community_and_social_initiatives", "b2b_contract", 
    "employment_contract", "mandate_contract", "substitution_agreement", 
    "work_contract", "agency_agreement", "temporary_staffing_agreement", 
    "specific_work_contract", "internship_apprenticeship_contract", 
    "temporary_employment_contract", "language_english", "language_german", 
    "language_french", "language_spanish", "language_italian", 
    "language_dutch", "language_russian", "language_chinese_mandarin", 
    "language_japanese", "language_portuguese", "language_swedish", 
    "language_danish", "internship", "junior", "middle", "senior", "lead", 
    "full_time", "hybrid", "remote", "upload_id", "expiration", "url", 
    "date_posted"
]

PLOT_COLUMNS = [
    'ID', 'JobTitle', 'CoreRole', 'Employer', 'City', 'Latitude', 'Longitude',
    'Region', 'StartSalary', 'MaxSalary', 'Technologies', 'Responsibilities',
    'Requirements', 'Offering', 'Benefits', 'WorkLifeBalance', 
    'FinancialRewards', 'HealthWellbeing', 'Development', 
    'WorkplaceCulture', 'MobilityTransport', 'UniqueBenefits', 
    'SocialInitiatives', 'B2BContract', 'EmploymentContract', 
    'MandateContract', 'SubstitutionAgreement', 'WorkContract', 
    'AgencyAgreement', 'TempStaffingAgreement', 'SpecificWorkContract', 
    'InternshipContract', 'TempEmploymentContract', 'English', 
    'German', 'French', 'Spanish', 'Italian', 
    'Dutch', 'Russian', 'Mandarin', 'Japanese', 
    'Portuguese', 'Swedish', 'Danish', 'Internship', 
    'Junior', 'Middle', 'Senior', 'Lead', 'FullTime', 'Hybrid', 
    'Remote', 'UploadID', 'Expiration', 'URL', 'DatePosted'
]

PROFESSION_TITLES = [
    "Frontend Engineer", "Manual Tester", "Full Stack Software Engineer",
    "Java Software Developer", "Business Development Manager", "Test Coordinator",
    "Cybersecurity Researcher", "Software Engineer", "DevOps Engineer",
    "Product Owner", "Business Analyst", "QA Automation Engineer",
    "IT Support Specialist", "System Analyst", "Data Engineer", "Backend Engineer",
    "Cloud Engineer", "Software Developer", "Network Administrator", 
    "Technical Support Engineer", "Frontend Developer", "Full Stack Developer",
    "System Engineer", "UX/UI Designer", "IT Project Manager", 
    "Database Administrator", "Solution Architect", "IT Security Specialist",
    "Cloud Architect", "M365 Security Support Specialist", "Python Developer",
    "Java Developer", "ERP Administrator", "Data Scientist", "System Administrator",
    "SAP Consultant", "Embedded Software Engineer", "Business Intelligence Analyst", 
    "Database Specialist", "Mobile Developer", "IT Consultant", "Automation Tester",
    "DevSecOps Engineer", "Cloud DevOps Engineer", "Service Desk Analyst", 
    "Machine Learning Engineer", "Integration Developer", "Fullstack Developer",
    "Service Manager", "Product Manager", "UX Designer", "AI Engineer",
    "Business Consultant", "Customer Success Manager", "Cloud Security Expert", 
    "Data Analyst", "Project Manager", "Technical Consultant", "Cybersecurity Analyst",
    "Test Engineer", "System Architect", "Security Engineer", "UX/UI Designer", 
    "Release Manager", "Data Architect", "Network Engineer", "Platform Engineer", 
    "Cloud Solutions Architect", "IT Security Architect", "Automation Engineer", 
    "Backend Developer", "Agile Business Analyst", "BI Analyst", 
    "Business Operations Analyst", "Compliance Specialist", "Credit Risk Modelling Expert",
    "Customer Support Specialist", "Data Governance Analyst", "Data Science & Business Analyst", 
    "Database Developer", "Delivery Manager", "Desktop Engineer", "DevOps/SRE", 
    "Embedded Application Developer", "Engineering Manager", "ERP Director", 
    "Frontend Angular Developer", "Full Stack AI Developer", "Golang Developer", 
    "IT Business Analyst", "IT Help Desk", "IT Manager", "IT Security Officer", 
    "IT Solution Architect", "IT Specialist", "Java Backend Developer", 
    "Java Software Engineer", "Javascript Frontend Developer", "LQA Game Tester", 
    "Machine Learning Engineer", "MID Back-End Developer", "MID DevOps Engineer", 
    "MID Frontend Developer", "Microsoft Azure Customer Success - AI", "Mobile Manual Tester", 
    "Network Operation Center Engineer", "Node.js Developer", "Operation M365 Analyst", 
    "PHP Developer", "Power Apps Consultant", "Power BI Developer", "Principal Data Engineer", 
    "Product Analyst", "Product Designer", "Product Management Consultant", 
    "Programmer .Net", "Programmer Aplikacji ERP", "Programmer Delphi", "Programmer ETL", 
    "Programmer Java", "Programmer PHP", "Programmer Pl/SQL", "Programmer SQL", 
    "Python Engineer", "QA Engineer", "React Developer", "React Native Developer", 
    "Release Manager", "Ruby on Rails Developer", "Salesforce Consultant", 
    "Salesforce Developer", "SAP Abap Developer", "SAP Basis Administrator", 
    "SAP Consultant", "SAP Developer", "SAP EWM Consultant", "SAP Fico Consultant", 
    "SAP Project Manager", "Scrum Master", "Security Consultant", "Security Specialist", 
    "Service Desk Specialist", "ServiceNow Developer", "Sharepoint Developer", 
    "Site Reliability Engineer", "Software Architect", "Software Engineering Manager", 
    "Software Tester", "Solution Engineer", "SQL Developer", "Staff Software Engineer", 
    "Support Engineer", "System Administrator Kafka", "System Architect", 
    "System Designer", "System Integration Test Engineer", "System Support Engineer", 
    "Technical Consultant", "Technical Product Owner", "Technical Support Specialist", 
    "Test Automation Engineer", "Tester Oprogramowania", "User Support Specialist", 
    "Visual Designer", "Web Developer", "Wordpress Developer", "Architect", 
    "Assistant Vice President - Data Analytics", "AWS DevOps Engineer", 
    "Azure Cloud Platform Engineer", "Azure Data Engineer", "Azure DevOps Engineer", 
    "BI Consultant / BI Developer", "Blockchain Developer", "Business Intelligence Developer", 
    "Citrix Engineer", "Cloud Data Engineer", "Cloud Database Engineer", "Cloud IAC DevOps", 
    "Computer Servicer", "Customer Acquisition Manager", "Customer Care Process & Product Specialist", 
    "Customer Service Consultant", "Cyber Threat Intelligence Analyst", 
    "Cybersecurity Controls Oversight Manager", "Data & AI Co-Owner", 
    "Data Analyst / SQL Developer", "Data Leakage Prevention Specialist", 
    "Data Security Automation SME", "Data System Analyst", "Database Analyst", 
    "Database Consultant", "Delivery Specialist", "Desktop / Mobile Software Developer - Fintech / Crypto", 
    "DevOps Azure - MS System Administrator", "Embedded Software Developer - Fintech / Crypto", 
    "ERP Administrator", "ERP Consultant", "ERP Project Manager", "Full Stack Developer", 
    "Full Stack Software Engineer", "Functional SW Developer", "Guidewire Developer", 
    "Head of IT Department", "HTML Design Specialist", "Implementation Consultant", 
    "Information Security Analyst", "Administrator IT", "Web Application Support Specialist", 
    "IT Architect", "IT Business Consultant", "IT Consultant", "IT Network Specialist", 
    "IT Project Manager", "IT Security Specialist", "IT Service Desk Consultant", 
    "Java Engineering", "Javacard Applet Developer", "Kotlin Software Developer", 
    "Lead Software Engineer", "Linux Engineer", "Machine Learning Engineer", 
    "Main Architect of Digital Channels", "Master Data Analyst", "MID Back-End Developer", 
    "Mobile Developer", "ML Product Manager", "Integration Architect", "Network Engineer", 
    "Node.js Developer", "Operation M365 Analyst", "Operations Manager", "PHP Developer", 
    "Platform Engineer", "Power Platform Developer", "Principal Back-End Software Engineer", 
    "Principal Data Engineer", "Product Designer", "Product Manager", "Programmer / BI Developer", 
    "Programmer / Deweloper C#", "Programmer Aplikacji ERP", "Programmer Delphi", 
    "Programmer ETL", "Programmer Front-End", "Programmer Java", "Python Developer", 
    "Python Engineer", "Quality Analyst", "Release Manager", "Ruby on Rails Developer", 
    "SAP Abap Developer", "SAP Basis Administrator", "SAP Fico Consultant", "SAP Project Manager", 
    "Security Engineer", "Senior Software Engineer", "Service Desk Specialist", 
    "Sharepoint Developer", "Site Reliability Engineer", "Software Architect", 
    "Software Engineering Manager", "Software Tester", "Solution Architect", 
    "SQL Developer", "Staff Software Engineer", "Support Engineer", "System Administrator", 
    "System Integration Test Engineer", "Technical Consultant", "Technical Support Engineer", 
    "Test Automation Engineer", "Test Engineer", "UX Researcher", "UX/UI Designer", 
    "Visual Designer", "Web Developer", "Wordpress Developer", "MLOps Engineer", 
    "Service Consultant", "Data Annotator", "C++ Developer", "Infrastructure Engineer", 
    "Oracle Developer", "Vue.js Developer", "iOS Engineer", "iOS Developer", 
    "Scala Developer", "Hardware Engineer", "TypeScript Developer", "Shopify Developer", 
    "Smalltalk Developer", "C# Developer", "Staff Engineer", "Symfony Developer", 
    "Cross-Platform Developer", "Virtualization Engineer", "Networks/Systems Engineer", 
    "Software Support Engineer", "Next.js Developer", "Support Specialist", "GRC Analyst", 
    "Business Process Engineer", "Reporting Specialist", "Apex Developer", "Mainframe Developer", 
    "Business Analytics & Reporting Specialist", "Angular Developer", "Senior Mainframe Developer", 
    "Specialist Intranet Management (SharePoint Online)", "Architect of IT Systems", 
    "Software Engineer - Platform", ".NET Developer", "PowerApps Developer", 
    "GO Developer (Distributed System, blockchain)", "Angular Developer", "DevOps Oracle Specialist", 
    "Apex Developer", "JavaScript / Solidity Developer (DeFi)", "Administrator Solaris/AIX", 
    "Unix Administrator", "Electrical & Electronic Engineer", "Level Designer", 
    "Security Expert", "Team Coordinator", "Open Source Engineer", "Data Visualization Specialist", 
    "Internal Manager", "ETL Developer", "Uplift Engineer", "Graphic Designer", 
    "Infrastructure Analyst", "Tester Salesforce", "Xamarin / Maui Developer"
]

TRANSLATION_DICT = {
    "analityk": "Analyst",
    "młodszy": "Junior",
    "programista": "Developer",
    "sieci": "Network",
    "inżynier": "Engineer",
    "automatyki": "Automation",
    "specjalista": "Specialist",
    "konsultant": "Consultant",
    "konsultantka": "Consultant",
    "systemu": "System",
    "architekt": "Architect",
    "manualny": "Manual",
    "informatyki": "IT",
    "analityczka": "Analyst",
    "technik serwisu" : "Service Technician",
    "programistka" : "Developer",
}

PROJECT_DESCRIPTION = (
    "Welcome to my first major project, a Polish IT jobs aggregator designed to help job seekers find their ideal IT positions.\n\n"
    "This tool scrapes job data from major Polish websites: pracuj.pl, bulldogjob.pl, and theprotocol.it.\n\n"
    "Whether you're a job seeker eager to find the perfect IT role or simply exploring opportunities in the Polish job market, this aggregator is tailored to provide you with up-to-date and comprehensive job listings.\n\n"
    "For detailed (technical) information about the project, please visit the repository:\n"
    "🔗 <a href='https://github.com/makararena/Polish-IT-Jobs-Aggregator'>GitHub Repository</a>\n\n"
    "🔗 <b>Connect with Me</b>:\n"
    "GitHub: <a href='https://github.com/makararena'>GitHub</a>\n"
    "LinkedIn: <a href='https://www.linkedin.com/in/makar-charviakou-b72526279/'>LinkedIn</a>\n"
    "📧 Gmail: makararena@gmail.com\n\n"
    "I am currently job hunting, so if you know of any IT opportunities, please let me know! 🥺🥺🥺"
)

WELCOME_MESSAGE = (
    "👋 Welcome to the IT Jobs Bot!\n\n"
    "🔍 Find the latest IT job postings easily by searching for specific job titles, experience levels, and more.\n\n"
    "ℹ️ Want to know more about this project? Tap 'About Project' for details.\n\n"
    "⚠️ If you encounter any issues, just type /start to reset the bot."
)

NO_FILTERS_MESSAGE = "⚠️ It looks like you haven't set any filters.\n\nIf you'd like to view all data:\n1. Go to the main menu and select Yesterday's Jobs to see yesterday's statistics.\n2. Choose Jobs by Date to view statistics for a specific date."

lAGUAGE_OPTIONS = [
        "English 🇬🇧", 
        "German 🇩🇪", 
        "French 🇫🇷", 
        "Spanish 🇪🇸",
        "Italian 🇮🇹", 
        "Dutch 🇳🇱", 
        "Russian 🇷🇺", 
        "Mandarin 🇨🇳",
        "Japanese 🇯🇵", 
        "Portuguese 🇵🇹", 
        "Swedish 🇸🇪", 
        "Danish 🇩🇰"
    ]

NOT_VALID_TECHNOLOGIES = {
    'LESS', 'PROJECT', 'DESIGN', "WINDOWS", "SUPPORT", "DATA", "DATABASE", "TEAMS",
    "DATABASES", "MICROSOFT", "NIST", "MEET", "BPMN", "APPLICATIONS", "MAST", "ENGLISH",
    "BUSINESS ANALYSIS", "DEVELOPMENT", "MANAGEMENT", "ANALYSIS", "PROJECT MANAGEMENT", "PROJECTS",
    "VMWA", "SNOW", "CODE"
}

KEEP_TECHNOLOGIES = {
    'C#', 'AWS', 'ERP', 'API', 'CSS', 'IOS', 'C++', 'SAP', 'GIT', 'SQL', 'PHP', 
    'XML', 'SSH', 'TLS', 'JWT', 'DNS', 'EC2', 'S3', 'RDS', 'VPC', 'ELB', 'IAM', 
    'PWA', 'CMS', 'CRM', 'IoT', 'TCP', 'UDP', 'GPU', 'SDK', 'SaaS', 'GCP', 'ICT', 
    'RCP', 'JIRA', 'VR', 'IPSEC', 'VPN', 'LAN', 'WAN', 'APIs', 'CDN', 'FTP', 'NFS', 
    'SLA', 'DDoS', 'DRM', 'CLI', 'NAT', 'XSS', 'SSL', 'BGP', 'AES', 'FaaS', 'RPA', 
    'BI', 'ETL', 'CI', 'CD', 'AI', 'ML', 'QA', 'KPI', 'B2B', 'B2C', 'SEO', 'SEM', 
    'P2P', 'SMS', 'MFA', 'SDK', 'USB', 'OS', 'UX', 'ID', 'DB', 'VIM', 'GUI', 
    'CPU', 'RAM', 'SSD', 'DNS', 'IO', 'CGI', 'WWW', 'RPG', 'SRE', 'IAM', 'EFS',
    'ORM', 'DMZ', 'UDP', 'SAS', 'EAI', 'ALM', 'AMQ', 'ESP', 'CRT', 'IAM', 'VFX',
    'JWT', 'API', 'VNC', 'XLM', 'IP', 'VR', 'IPX', 'B2G', 'PST', 'ISO', 'IR', 
    'SMP', 'DFS', 'RPC', 'ASP', 'SIM', 'CDR', 'TLD', 'AVX', 'HDD', 'SPD', 'DDR', 
    'DMA', 'SSD', 'CRT', 'DAC', 'HD', 'DLT', 'CDP', 'WAF', 'APT', 'IDS', 'IPS', 
    'MPL', 'MLP', 'ZFS', 'AD', 'DC', 'OSX', 'LVM', 'PDF', 'JVM', 'POD', 'SCM',
    'LXC', 'EXE', 'JRE', 'NPM', 'UDP', 'PPT', 'USB', 'RTS', 'BGP', 'PKI', 'DLP',
    'I/O', 'ABI', 'EEP', 'RFC', 'SDI', 'KVM', 'PCI', 'ECC', 'LCD', 'TFT', 'LED',
    'XOR', 'AES', 'RSA', 'SHA', 'GFS', 'STP', 'QOS', 'DHCP', 'PIP', 'TUN', 'TSL', 
    'SSL', 'MAC', 'PPP', 'IIS', 'OCR', 'CAD', 'CAM', 'DFS', 'CRT', 'TTL'
}


PROJECT_DESCRIPTION = (
    "Welcome to the IT Jobs Dashboard! 🚀\n\n"
    "This dashboard is your gateway to analyzing, using, and working with job postings for the timeframe you want. "
    "You can explore key job details such as locations, roles, salary ranges, required skills, and much more. You can also easily download all the data with your own filters, "
    "and generate the most important graphs based on your needs.\n\n"
    "🏢 **How It Works**:\n\n"
    "Every day, my web scrapers visit the most popular Polish IT websites to gather crucial data. This data is then "
    "processed and stored in my DWH. From there, you can access the final data as an Excel/CSV file or visualize it through graphs.\n\n"
    "This project is perfect for AI applications requiring large datasets, or for professionals looking to easily "
    "filter IT jobs by role, experience, and location. You could even create your own bot to apply for these jobs automatically! 🤖\n\n"
    "If you want to know more about this project, feel free to contact me privately. Please note, I cannot share the full "
    "program code to protect the integrity of the websites involved.\n\n"
    "By the way, I am looking for a job right now, and if you are an IT programmer in any company, could you please recommend me? 🥺🥺🥺"
)

DARK_THEME = {
    "custom_colorscale": [
        [0, 'rgb(26, 26, 51)'],   # Deep dark blue-black
        [0.5, 'rgb(51, 51, 102)'],  # Medium dark blue
        [1, 'rgb(102, 102, 153)']   # Light blue
    ],
    "template": "plotly_dark",
    "style": "carto-darkmatter",
    "landcolor": 'rgb(10, 10, 10)',      # Almost black
    "oceancolor": 'rgb(0, 0, 50)',       # Deep blue for oceans
    "lakecolor": 'rgb(0, 0, 70)',        # Darker lake color
    "countrycolor": 'rgb(255, 255, 255)', # White for countries
    "coastlinecolor": 'rgb(255, 255, 255)', # White coastline
    "border_color": 'rgb(255, 255, 255)'   # White border
}

LIGHT_THEME = {
    "custom_colorscale": [
        [0, 'rgb(239, 237, 245)'],  # Light lavender
        [0.5, 'rgb(188, 189, 220)'],  # Medium lavender
        [1, 'rgb(117, 107, 177)']     # Deep purple
    ],
    "template": "plotly",
    "style": "carto-positron",
    "landcolor": 'rgb(242, 242, 242)',    # Very light gray
    "oceancolor": 'rgb(217, 234, 247)',   # Light blue for oceans
    "lakecolor": 'rgb(200, 225, 255)',    # Pale blue for lakes
    "countrycolor": 'rgb(200, 200, 200)', # Light gray for countries
    "coastlinecolor": 'rgb(150, 150, 150)', # Gray coastline
    "border_color": 'rgb(255, 255, 255)'   # White border
}

LANGUAGES_LIST = [
    'language_english', 'language_german', 'language_french', 
    'language_spanish', 'language_italian', 'language_dutch', 
    'language_russian', 'language_chinese_mandarin', 
    'language_japanese', 'language_portuguese', 'language_swedish', 
    'language_danish'
]

CONTRACTS_LIST = [
    'b2b_contract', 'employment_contract', 'mandate_contract', 
    'substitution_agreement', 'work_contract', 'agency_agreement', 
    'temporary_staffing_agreement', 'specific_work_contract', 
    'internship_apprenticeship_contract', 'temporary_employment_contract'
]

CONTRACT_LIST_DF = [
    'B2B Contract', 'Contract of Employment', 'Contract of Mandate', 
    'Substitution Agreement', 'Contract of Work', 'Agency Agreement', 
    'Temporary Staffing Agreement', 'Contract for Specific Work', 
    'Internship / Apprenticeship Contract', 'Contract of Temporary Employment'
]

BENEFITS_LIST = [
    'work_life_balance', 'financial_rewards_and_benefits', 
    'health_and_wellbeing', 'personal_and_professional_development', 
    'workplace_environment_and_culture', 'mobility_and_transport', 
    'unique_benefits', 'community_and_social_initiatives'
]

EXPERIENCES_LIST = [
    'junior', 'middle', 'senior', 'programmist', 'lead', 
    'team leader', 'team lead'
]