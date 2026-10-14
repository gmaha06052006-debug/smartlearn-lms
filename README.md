# SmartLearn — Intelligent Learning Management System

> **A Complete Python Full-Stack Learning Management System (LMS)** built with Django, Django REST Framework, Bootstrap 5, JavaScript, Chart.js, and MySQL.  
> Directly translated from the visual design language of **placed-ai-main-2** into a production-grade full-stack Django architecture.

---

## 🌟 Highlights & Features

### 1. Multi-Role Authorization & Security
- **Student Role**: Personalized portal, course enrollment, interactive video lectures, assignment turn-in, timed quiz taking, smart study recommendations, and visual learning analytics.
- **Faculty Role**: Course syllabus authoring, assignment deliverables creation, student submission review, custom feedback and scoring.
- **Administrator Role**: Cross-platform console, user and role management, course publishing controls, audit logs, and institutional health metrics.

### 2. Core Learning Management
- **Course Catalog**: Categorized course catalog with real-time keyword search and difficulty filters (Beginner, Intermediate, Advanced).
- **Curriculum & Lesson Player**: Structured modules and lessons with embedded video playback, downloadable starter files, and AJAX progress checkoffs.
- **Automated Progress Tracking**: Real-time progress bar recalculation per course as lessons are completed.

### 3. Assessments & Evaluation
- **Timed Quizzes**: Dynamic countdown timer with auto-submit mechanism on expiration.
- **Instant Scoring & Review**: Automated pass/fail calculations, scorecard metrics, and full question explanations.
- **Practical Assignments**: File upload drop zone supporting `.pdf`, `.docx`, and `.zip` submissions with faculty grading and comments.

### 4. Intelligence & Insights
- **Smart Recommendation Engine**: Context-aware recommendation algorithms analyzing upcoming assignment deadlines, uncompleted lessons, and spaced repetition quizzes.
- **Learning Analytics Dashboard**: Interactive completion charts rendered with **Chart.js**, study session logs, and activity feeds.
- **Institutional Broadcasts**: Targeted announcements and alert notifications for students and faculty.

### 5. Production RESTful API
- Complete Django REST Framework endpoints under `/api/` with token/session authentication and JSON responses for all resources.

---

## 🎨 UI/UX Design System (Replicating placed-ai-main-2)
- **Palette**:
  - Warm Cream Background: `#F6F3EC`
  - High-Contrast Primary: `#111111`
  - Signature Lime Accent: `#C7FF4A` (Hover: `#B8F13A`)
  - Subtle Borders: `#E5E5E5`
- **Typography**: Google Fonts Inter and Outfit.
- **Interactive Elements**: Floating stat cards with hover lift, pill buttons, responsive sidebar with mobile slide-in, and split-screen authentication screens.

---

## 🛠️ Technology Stack
- **Backend**: Python 3.13, Django 5.1+, Django REST Framework
- **Database**: MySQL (Default production) / SQLite (Local testing fallback)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons 1.11, Chart.js 4.4
- **Version Control**: Git & GitHub

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- MySQL Server (optional for production; SQLite fallback is supported out of the box)

### 2. Clone and Setup Environment
```bash
cd smartlearn_django
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Database
Copy `.env.example` to `.env`:
```ini
SECRET_KEY=smartlearn-super-secret-key-prod-2026-secure
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Configuration:
USE_SQLITE=False
DB_NAME=smartlearn_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Or use SQLite for quick local evaluation:
# USE_SQLITE=True
```

### 4. Apply Migrations & Seed Demo Data
```bash
python manage.py makemigrations accounts courses assignments quizzes analytics recommendations notifications
python manage.py migrate
python manage.py seed_data
```

### 5. Run Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 👥 Demo Accounts

| Role | Email / Username | Password | Access Area |
| :--- | :--- | :--- | :--- |
| **Student** | `student@smartlearn.com` | `student123` | Student Dashboard (`/dashboard/`) |
| **Faculty** | `dr.smith@smartlearn.com` | `faculty123` | Faculty Portal (`/faculty/dashboard/`) |
| **Administrator** | `admin@smartlearn.com` | `admin123` | Admin Console (`/admin-dashboard/` & `/admin-panel/`) |

---

## 🧪 Running Automated Tests
```bash
python manage.py test
```

---

## 📁 Repository Structure
```
smartlearn_django/
├── config/                 # Root settings, URLs, WSGI, ASGI
├── accounts/               # User profiles, authentication, signals
├── courses/                # Courses, modules, lessons, enrollments, seed command
├── assignments/            # Assignments, submissions, grading
├── quizzes/                # Timed quizzes, questions, auto-grading
├── analytics/              # Study sessions, activity logs, Chart.js APIs
├── recommendations/        # Algorithmic recommendation engine
├── notifications/          # Alerts and campus-wide broadcasts
├── static/
│   ├── css/smartlearn.css  # Design system matching placed-ai-main-2
│   └── js/                 # Sidebar, AJAX progress, quiz timer
├── templates/              # Bootstrap 5 & Django templates
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```
