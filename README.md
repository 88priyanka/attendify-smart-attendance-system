# 🕒 Attendify – Smart Employee Attendance & Anomaly Detection System

Attendify is a **Smart Employee Attendance Management System** built with Python and Streamlit. It helps organizations manage employee attendance, monitor working hours, analyze attendance patterns, and identify unusual attendance behavior through an interactive dashboard.

## 🚀 Live Demo

👉 **[Open Attendify Live App](https://attendify-smart-attendance-system-jvf9jq76mctssjyrbq2fwd.streamlit.app/)**

The application is deployed using **Streamlit Community Cloud**, which provides each deployed app with a shareable `streamlit.app` URL.

## ✨ Features

* 🔐 Role-based login system
* 👨‍💼 Employee management
* 🕒 Employee attendance tracking
* 📊 Company attendance dashboard
* 📈 Attendance analytics
* ⏱️ Working-hours monitoring
* 🟠 Late attendance tracking
* 🚨 Attendance anomaly detection
* 📋 Employee attendance history
* 📊 Interactive charts and visualizations
* 🗃️ SQLite database integration
* 🎨 User-friendly Streamlit interface

## 👥 User Roles

### 👑 Admin

* Manage employees
* View company attendance
* Monitor attendance analytics
* Detect attendance anomalies

### 👨‍💼 Manager

* View employee attendance
* Monitor department/company attendance
* Analyze attendance patterns
* View anomaly information

### 👤 Employee

* View personal dashboard
* Check attendance records
* Monitor personal attendance history

## 🛠️ Technologies Used

| Technology | Purpose                             |
| ---------- | ----------------------------------- |
| Python     | Application development             |
| Streamlit  | Web application and dashboard       |
| SQLite     | Database management                 |
| Pandas     | Data processing and analysis        |
| Plotly     | Interactive data visualization      |
| Bcrypt     | Password hashing and authentication |

## 📂 Project Structure

```text
attendify-smart-attendance-system/
│
├── app.py
├── database.py
├── auth.py
├── attendance.py
├── employee_management.py
├── requirements.txt
│
├── data/
│   └── attendance.db
│
└── pages/
```

## 📦 Requirements

```text
streamlit
pandas
plotly
bcrypt
```

The deployment environment installs the packages listed in `requirements.txt`; Streamlit's deployment documentation recommends declaring the additional Python packages your application needs there.

## ▶️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/attendify-smart-attendance-system.git
```

### 2. Open the project

```bash
cd attendify-smart-attendance-system
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔄 Application Flow

```text
Login
  ↓
Role Verification
  ↓
Dashboard
  ↓
Attendance Management
  ↓
Attendance Analytics
  ↓
Anomaly Detection
  ↓
Reports & Monitoring
```

## 🎯 Project Objective

The main objective of Attendify is to provide a simple digital solution for employee attendance management while using data analysis to identify attendance patterns and unusual behavior.

## 💡 Key Highlights

* Real-world employee attendance use case
* Role-based access control
* Secure password hashing using Bcrypt
* Database-driven attendance management
* Interactive analytics dashboard
* Anomaly detection functionality
* Cloud deployment with Streamlit

## 🌐 Deployment

**Platform:** Streamlit Community Cloud

**Live Application:**
https://attendify-smart-attendance-system-jvf9jq76mctssjyrbq2fwd.streamlit.app/

Streamlit Community Cloud supports deploying an application directly from a GitHub repository and provides a unique `streamlit.app` URL for the deployed application.

## 👩‍💻 Developer

**Priyanka**

Built as a real-world Python-based project to demonstrate application development, database management, data analysis, visualization, authentication, and cloud deployment.
