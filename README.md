# Traffic IQ- Intelligent Traffic Monitoring, Load Balancing & Advertisement Analytics System

## Live Website:
[TrafficIQ Live Dashboard](https://trafficiq-iunw.onrender.com?utm_source=chatgpt.com)

---

# Brief Description

TrafficIQ is a full-stack web-based traffic analytics and monitoring platform designed to analyze, visualize, and manage traffic-related data in real time. The system provides interactive dashboards, security monitoring, user behavior analytics, traffic load analysis, and automated PDF report generation.

The platform helps administrators and organizations gain meaningful insights using graphical visualizations, cloud database integration, and smart reporting systems.

---

# Technology Stack & Tools Used

## Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

## Backend

* FastAPI
* Uvicorn

## Database & Cloud

* PostgreSQL
* [Supabase] (https://gedgbntxcurvdrzrvxtj.supabase.co)

## Data Processing & Analytics

* Pandas
* NumPy

## Authentication & Security

* JWT Authentication
* bcrypt Password Hashing

## Reporting

* ReportLab PDF Generation

## Deployment & Version Control

* [Render](https://trafficiq-iunw.onrender.com)
* [GitHub](https://github.com/Mayank1705-web/TrafficIQ.git)
* Git

## Development Tools

* VS Code
* PyCharm

---

# Features & Functionalities Implemented

## Authentication System

* User Signup & Login
* Secure JWT Authentication
* Password Encryption using bcrypt

## Traffic Analytics Dashboard

* Real-Time Traffic Monitoring
* Interactive Graphs & Charts
* Traffic Pattern Visualization

## Load Analysis

* Traffic Load Monitoring
* Performance Insights
* Data Representation through Charts

## Security Monitoring

* Security Log Tracking
* Suspicious Activity Monitoring
* Security Analytics Dashboard

## User Behavior Analytics

* User Activity Analysis
* Behavioral Insights
* User Engagement Tracking

## Advertisement Analytics

* Ad Performance Monitoring
* Traffic Conversion Analysis
* Advertisement Reports

## Automated PDF Report Generation

* Downloadable Reports
* Timestamped Reports
* Dynamic Data Reports

## Cloud Database Integration

* Supabase PostgreSQL Integration
* Optimized Database Connection Pooling

## REST API Support

* FastAPI-Based APIs
* Efficient Backend Communication

---

# Installation & Execution Steps

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/TrafficIQ.git
cd TrafficIQ
```

---

## 2️. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️. Configure Environment Variables

Create a `.env` file and add:

```env
DATABASE_URL=your_supabase_postgresql_url
SECRET_KEY=your_secret_key
```

---

## 5️. Run the Backend Server

```bash
cd Scripts
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

---

## 6️. Open the Frontend

Open the frontend files from the `Dashboard` folder in your browser.

Example:

```plaintext
Dashboard/index.html
```

---

# Project Structure

```plaintext
TrafficIQ/
│
├── Dashboard/
│   ├── assets/
│   │   └── profiles/
│   │       ├── anreta.png
│   │       ├── anshul.png
│   │       ├── mayank.png
│   │       ├── shantilal.jpg
│   │       └── shantilal.png
│   │
│   ├── css/
│   │   ├── aboutus.css
│   │   ├── login_css.css
│   │   ├── signup_css.css
│   │   └── styles.css
│   │
│   ├── data/
│   │   ├── ads_summary.json
│   │   ├── load_summary.json
│   │   ├── log_summary.json
│   │   ├── traffic_summary.json
│   │   └── user_summary.json
│   │
│   ├── images/
│   │   ├── Anshuli.jpg
│   │   ├── Mayank Ingole.jpg
│   │   └── Prof. Shantilal Bhayal.enc
│   │
│   ├── js/
│   │   ├── ads_charts.js
│   │   ├── auth.js
│   │   ├── charts.js
│   │   ├── common.js
│   │   ├── config.js
│   │   ├── dashboard.js
│   │   ├── load_chart.js
│   │   ├── login.js
│   │   ├── security.js
│   │   ├── security_charts.js
│   │   ├── signup.js
│   │   ├── theme.js
│   │   └── users_charts.js
│   │
│   └── pages/
│       ├── about.html
│       ├── ads.html
│       ├── configuration.html
│       ├── index.html
│       ├── load.html
│       ├── login.html
│       ├── reports.html
│       ├── security.html
│       ├── signup.html
│       ├── traffic.html
│       └── users.html
│
├── Data/
│   ├── Processed/
│   │   ├── ads_clean.csv
│   │   ├── logs_clean.csv
│   │   ├── retail_clean.csv
│   │   ├── traffic_clean.csv
│   │   └── user_behavior_clean.csv
│   │
│   └── Raw/
│       ├── ad_data.csv
│       ├── logfiles.log
│       ├── online_retail_sales.csv
│       ├── server_log.csv
│       ├── traffic_data.csv
│       └── user_behaviour.csv
│
├── Database/
│   └── trafficIQ_users.db
│
├── Reports/
│
├── Scripts/
│   ├── ad_analytics.py
│   ├── api.py
│   ├── auth.py
│   ├── dashboard_api.py
│   ├── data_cleaning.py
│   ├── db.py
│   ├── import_to_supabase.py
│   ├── load_analysis.py
│   ├── optimize_project.py
│   ├── report_generator.py
│   ├── security_logs.py
│   ├── traffic_analysis.py
│   ├── update_fixes.py
│   ├── update_theme.py
│   ├── update_theme_placement.py
│   └── user_behavior_analysis.py
│
├── .gitignore
├── requirements.txt
├── README.md
└── .env
```

---

# Project Screenshots / Output

## Dashboard Interface

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/11b07926-2c7d-45c7-a40b-529dfe2b719e" />*

## Traffic Analytics Graph

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e78ec836-71a6-4e6f-ae6e-12dcff90749c" />*

## Load Intelligence

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9be651a2-e53c-452d-b490-9eded26ac035" />*

## Ad Analysis

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/025c3361-cab7-4c36-9916-d3525696c393" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/cbca095e-4a59-4df9-bc1d-e4278c9cf8a7" />*

## User Behavior

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/38b99879-c93f-4dc2-a801-01e53eaff2b4" />*

## Security Logs

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/cf270d78-63ac-43e8-8983-a7bb2a19de14" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f7e9157e-4182-4de7-a033-11a87ceed4af" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/439fc7d8-3487-44c8-a68d-842e30bca657" />*

## Configuration (To be developed)

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/95097db1-2174-4fde-a1ae-4a2cf02d777f" />*

## Business Report

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1fc44361-3409-4879-8ad1-0f82fa8ffcd6" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6b62cc44-de3a-4a4d-a7e6-43038568c850" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/028cd8ca-a022-4c34-b1da-df2dd7f46370" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/2b0e22ed-a9b9-4978-a378-637ed17c52f1" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/35a9a6d7-0a73-4854-8c40-09a1eef68e53" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/2c10bd26-c096-4166-af4e-b6c80647d644" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4b539eee-e5d8-436d-9fd8-ce5c6dedeb2e" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/8a53cc01-4528-45aa-ad03-0b32c10584b9" />*
*[TrafficIQ_Business_Report.pdf](https://github.com/user-attachments/files/28319076/TrafficIQ_Business_Report.pdf)*

## About Us

*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/eb3d3488-9b5e-4e25-8960-a3bb95a8b5ea" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/5b4e0f65-c56e-4b0b-b4a7-6d6bce0926b9" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/d40b5998-adb2-46e4-805a-596cf8ce2beb" />*
*<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/81e6d0bd-5780-471a-aa7e-082ffbf1084c" />*

---

# Team Members

| Name            | Role                                                            |
| --------------- | --------------------------------------------------------------- |
| Mayank Ingole   | Frontend Development, Backend Development & Database Management |
| Anshuli Chouhan | Frontend Development, Backend Development & Database Management |

---

# Future Enhancements

* AI-Based Traffic Prediction
* IoT-Based Real-Time Traffic Integration
* Mobile Responsive Dashboard
* Advanced Data Visualization
* Live Alert & Notification System

---

# Conclusion

TrafficIQ is a smart traffic analytics and monitoring platform that combines full-stack development, cloud deployment, data visualization, authentication, and automated reporting into one integrated solution. The project demonstrates practical implementation of modern web technologies, backend APIs, database systems, and analytics tools.

---

# Project Links

| Platform            | Link                                                                              |
| ------------------- | --------------------------------------------------------------------------------- |
| Live Website        | [TrafficIQ Dashboard](https://trafficiq-iunw.onrender.com)                        |
| Deployment Platform | [Render](https://render.com)                                                      |
| Database Platform   | [Supabase](https://supabase.com)                                                  |
