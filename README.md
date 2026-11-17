# Django Student Management System

[![Python](https://img.shields.io/badge/Python-3.13%20tested-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![GitHub stars](https://img.shields.io/github/stars/amreshchaurasiyatechedu/student-management-system?style=social)](https://github.com/amreshchaurasiyatechedu/student-management-system/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/amreshchaurasiyatechedu/student-management-system?style=social)](https://github.com/amreshchaurasiyatechedu/student-management-system/forks)
[![GitHub issues](https://img.shields.io/github/issues/amreshchaurasiyatechedu/student-management-system)](https://github.com/amreshchaurasiyatechedu/student-management-system/issues)

An educational Django application for managing students, staff, courses, attendance, results, academic sessions, leave requests, and feedback from role-specific dashboards.

**Maintained by [Amresh Chaurasiya](https://github.com/amreshchaurasiyatechedu).**

[View the project](https://github.com/amreshchaurasiyatechedu/student-management-system) · [Watch the demo](https://www.youtube.com/watch?v=kArCR96m7uo)

> Python 3.13 is the interpreter used to check this checkout; the project does not declare a minimum Python version.

## Table of contents

- [Overview](#overview)
- [Key features](#key-features)
- [Screenshots and demo](#screenshots-and-demo)
- [Technology stack](#technology-stack)
- [Project architecture](#project-architecture)
- [Database](#database)
- [Installation and setup](#installation-and-setup)
- [Environment configuration](#environment-configuration)
- [Authentication and demo accounts](#authentication-and-demo-accounts)
- [Tests](#tests)
- [Roadmap](#roadmap)
- [Security and best practices](#security-and-best-practices)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Overview

Django Student Management System is a server-rendered web application for common student and academic administration. It brings core records and workflows into one place: administrators can maintain people and academic structures, staff can record attendance and marks, and students can review their own attendance and results.

The project was developed for educational purposes while learning Django and is suitable as a learning resource or a starting point for an institution-specific system. Adapt and review it for your institution's requirements before relying on it for real student records.

## Key features

### Administrators (HOD)

- Dashboard with summary counts and charts for students, staff, courses, subjects, and attendance-related data.
- Create, edit, list, and delete staff, students, courses, and subjects.
- Manage academic sessions with optional names and custom start/end dates.
- Review attendance records by subject and academic session.
- Review and reply to student and staff feedback.
- Approve or reject student and staff leave requests.
- Update the administrator profile.

Academic session dates are used when recording and viewing attendance. A session cannot be deleted while students or attendance records refer to it; date changes are validated against existing attendance.

### Staff and teachers

- Staff dashboard with student, subject, attendance, and leave summaries.
- Take and update attendance for assigned subjects.
- Add or update student exam and assignment marks.
- Submit and review leave applications.
- Send feedback to the HOD and view replies.
- Update the staff profile.

### Students

- Student dashboard with attendance totals and attendance charts by subject.
- View attendance for subjects in the student's course, filtered by date range.
- View recorded subject exam and assignment results.
- Submit and review leave applications.
- Send feedback to the HOD and view replies.
- Update the student profile.

## Screenshots and demo

No screenshots are currently included in the repository. The entries below are placeholders for genuine captures; no mock or unrelated images are used.

| Screen | Suggested image path | Status |
| --- | --- | --- |
| Login page | `screenshots/login-page.png` | Screenshot not provided |
| Admin dashboard | `screenshots/admin-dashboard.png` | Screenshot not provided |
| Staff dashboard | `screenshots/staff-dashboard.png` | Screenshot not provided |
| Student dashboard | `screenshots/student-dashboard.png` | Screenshot not provided |
| Attendance management | `screenshots/attendance-management.png` | Screenshot not provided |
| Results management | `screenshots/results-management.png` | Screenshot not provided |

### Video demonstration

Click the thumbnail to watch the existing project demonstration on YouTube:

[![Watch the Django Student Management System demo](https://img.youtube.com/vi/kArCR96m7uo/hqdefault.jpg)](https://www.youtube.com/watch?v=kArCR96m7uo)

The suggested paths do not currently exist. Add your own authentic captures to a new `screenshots/` directory, then replace each status with an image link. No screenshots have been generated for this README.

## Technology stack

### Backend

[![Python](https://img.shields.io/badge/Python-3.13%20tested-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)

- Python 3.13 was used to check this checkout; the project does not declare a minimum Python version.
- Django 6.1.2 is pinned in `requirements.txt`.

### Frontend

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-4.4.1-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![AdminLTE](https://img.shields.io/badge/AdminLTE-3.0.5-3C8DBC)](https://adminlte.io/)
[![jQuery](https://img.shields.io/badge/jQuery-0769AD?logo=jquery&logoColor=white)](https://jquery.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

The interface uses Django templates, bundled static assets, and JavaScript for dashboard charts and asynchronous attendance workflows.

### Database

[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

SQLite is the database engine configured by `student_management_system/settings.py`. Although `mysql-connector-python` is present in the dependency file, the project settings do not configure MySQL.

### Libraries and dependencies

Python package versions are pinned in [`requirements.txt`](requirements.txt):

`asgiref`, `Django`, `django-extensions`, `graphviz`, `mysql-connector-python`, `protobuf`, `pydot`, `pyparsing`, `pytz`, `six`, `sqlparse`, and `tzdata`.

### Development tools

- Python and pip for creating the environment and installing dependencies.
- Git for retrieving the repository.
- Django management commands (`manage.py`) for migrations, the development server, system checks, and the test runner.

## Project architecture

```text
.
├── .gitignore                       # Excludes local secrets, database, uploads, and caches
├── manage.py
├── requirements.txt
├── static/                            # Bundled CSS, JavaScript, and image assets
├── student_management_system/
│   ├── settings.py                    # Settings, installed app, database, static/media paths
│   ├── urls.py                        # Project URL configuration and media serving
│   ├── asgi.py
│   └── wsgi.py
└── student_management_app/
    ├── models.py                     # Persistent application data models
    ├── forms.py                      # Academic session and student forms
    ├── urls.py                       # Application routes
    ├── views.py                      # Login, logout, and shared views
    ├── HodViews.py                   # HOD workflows
    ├── StaffViews.py                 # Staff workflows
    ├── StudentViews.py               # Student workflows
    ├── EmailBackEnd.py               # Email-based authentication
    ├── LoginCheckMiddleWare.py       # Role-aware view routing
    ├── migrations/
    ├── templates/
    │   ├── hod_template/
    │   ├── staff_template/
    │   └── student_template/
    └── tests.py
```

### Django components

- **`student_management_system`** is the Django project package. Its settings configure `student_management_app`, SQLite, the custom user model, authentication backend, templates, and static/media paths.
- **`student_management_app`** is the installed Django application. It contains the models, forms, migrations, URLs, role-specific views, authentication middleware/backend, templates, and tests.
- **Role-specific view modules** keep HOD, staff, and student request handlers separate. Templates are grouped by the same roles.
- **Static assets** are bundled in `static/`. User uploads use the runtime `media/` directory, which is ignored and not included in the published snapshot.

## Database

### Configured database

SQLite is the only database engine configured by this checkout. `student_management_system/settings.py` points Django at the repository-root `db.sqlite3` file. No external database service or database environment variable is required for local development. The local database file is ignored and will not be published; `python manage.py migrate` creates it locally.

The requirements file includes `mysql-connector-python`, but that package does not configure MySQL; the active Django database backend remains SQLite.

### Models and relationships

The schema is defined in `student_management_app/models.py` and evolved through the app's migrations:

- `CustomUser` extends Django's `AbstractUser` with a role value; `AdminHOD`, `Staffs`, and `Students` hold one-to-one role profiles.
- `Courses` connect to `Subjects` and `Students`. A subject references its course and assigned user.
- `SessionYearModel` stores academic session names and date boundaries. Students and attendance records reference a session.
- `Attendance` records a subject, session, and date. `AttendanceReport` links a student to an attendance record with a present/absent status.
- `StudentResult` links a student and subject with exam and assignment marks.
- `LeaveReportStudent` and `LeaveReportStaff` store leave requests and their statuses.
- `FeedBackStudent` and `FeedBackStaffs` store feedback and its reply. `NotificationStudent` and `NotificationStaffs` provide notification record models.

### Migrations

After installing dependencies and from the project root, apply all pending migrations with:

```bash
python manage.py migrate
```

This creates `db.sqlite3` if it is not present and applies migrations for Django and the application. The same command is used after pulling changes that add migrations.

### Main application workflow

1. A user submits an email and password on the login page; `EmailBackEnd.py` authenticates against the custom user model.
2. The user's role determines the destination dashboard. `LoginCheckMiddleWare.py` routes signed-in users to their role's view area.
3. Role-specific views read and update the app's models through Django's ORM; templates render the dashboards and management screens.
4. HOD users maintain staff, students, courses, subjects, and academic sessions. Staff record attendance and marks and submit leave or feedback. Students review attendance and results and submit leave or feedback.

## Installation and setup

### Prerequisites

- Python with `venv` and pip available. Python 3.13 was used to verify this checkout; the repository does not declare a minimum supported Python version.
- Git.

### Clone the repository

Run these commands from the parent directory where you want the project:

```bash
git clone https://github.com/amreshchaurasiyatechedu/student-management-system.git
cd student-management-system
```

### Create and activate a virtual environment

Use the commands for your shell from the project directory.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt (CMD)**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

With the virtual environment active:

```bash
python -m pip install -r requirements.txt
```

### Set `DJANGO_SECRET_KEY`

The application requires a secret key from the process environment. Generate a fresh key and set it in the current terminal session. Keep the value private; closing the terminal clears the session variable.

**Windows PowerShell**

```powershell
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Windows Command Prompt (CMD)**

Run this in an interactive Command Prompt. Use `%%i` instead of `%i` if you place the command in a batch file.

```bat
for /f %i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set "DJANGO_SECRET_KEY=%i"
```

**macOS / Linux**

```bash
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
```

### Configure the database and apply migrations

The project is configured to use SQLite at `db.sqlite3` in the project root. No database server or additional credentials are required for local development. Apply Django's built-in and application migrations:

```bash
python manage.py migrate
```

### Create an administrator account

Create your own Django superuser; do not use or publish shared default credentials:

```bash
python manage.py createsuperuser
```

The custom user model defaults to the HOD role. Sign in to the application using the account's email address and password.

### Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser. The application login is at `/`; Django's built-in admin site is available at `/admin/`.

## Environment configuration

The application reads `DJANGO_SECRET_KEY` from the process environment. `DEBUG`, `ALLOWED_HOSTS`, and the SQLite database path are configured in `student_management_system/settings.py`.

There is no `.env` loader, so a `.env` file will not configure the application and no `.env.example` is provided. The commands above set the key only for the current terminal session. Never put real passwords, keys, or credentials in README files or commit `.env` files.

## Authentication and demo accounts

The custom user model supports HOD (`1`), staff (`2`), and student (`3`) roles. Authentication uses email address and password. A newly created superuser defaults to the HOD role; the HOD dashboard is used to manage staff and student accounts.

No default demo accounts or passwords are documented. To prepare a demo, create a separate HOD account with `python manage.py createsuperuser`, then add staff and student accounts and fictitious records through the application. Use strong, unique passwords, avoid real student data, and do not publish or reuse demo credentials.

## Tests

Run the app's Django tests with:

```bash
python manage.py test student_management_app
```

The current test module covers academic session APIs and attendance/session date behavior.

## Roadmap

### Implemented

- Role-specific HOD, staff, and student dashboards.
- HOD management for staff, students, courses, subjects, and academic sessions.
- Attendance recording, updating, and student attendance views.
- Student exam and assignment results.
- Leave requests and HOD approval/rejection.
- Feedback submission and HOD replies.
- Email-based login and role-specific application routing.

### Potential future improvements

These are ideas for future work, not features currently provided:

- Outbound email notifications for relevant events.
- More advanced analytics and reporting.
- Export attendance and results to PDF or Excel.
- Further responsive UI improvements.
- Broader API coverage for application workflows; a session-year JSON API already exists.
- More granular role permissions and authorization tests.

## Security and best practices

This project is configured for local development and is not production-hardened. In `student_management_system/settings.py`, `DEBUG` is enabled and `ALLOWED_HOSTS` is empty. An older version of this checkout contained a development key in Git history; treat that key as compromised and rotate it. The new GitHub snapshot will use a fresh initial commit without the existing Git history.

- Never commit `.env` files, passwords, API keys, or other secrets.
- Keep `SECRET_KEY` private; load a new production key from secure configuration.
- Set `DEBUG=False` in production.
- Set `ALLOWED_HOSTS` to the exact hostnames used by the deployment; do not use an unrestricted wildcard.
- Use strong, unique passwords for HOD, staff, and student accounts. Do not publish working credentials.
- Use HTTPS and configure secure cookies and other Django deployment settings for the hosting environment.
- Run the Django deployment checks and review the official [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/) before going live.

These are recommendations, not a claim that all production security controls are already implemented.

## Contributing

Contributions and focused improvements are welcome. Before opening a pull request:

1. Fork the repository on GitHub.
2. Clone your fork and create a feature branch:

   ```bash
   git clone https://github.com/YOUR-USERNAME/student-management-system.git
   cd student-management-system
   git checkout -b feat/short-description
   ```

3. Make a focused change and add or update tests when behavior changes.
4. Run the relevant tests:

   ```bash
   python manage.py test student_management_app
   ```

5. Replace the sample username and file path below with your GitHub username and the files you changed, then commit and push:

   ```bash
   git add path/to/changed-file
   git commit -m "Describe your change"
   git push -u origin feat/short-description
   ```

6. Open a pull request from your branch to the project's repository. Include a clear summary and test results, and do not include credentials or real student data.

## License

Licensing information has not yet been specified. No root-level `LICENSE` file was present when this README was updated; do not assume a license is granted.

## Author

**Amresh Chaurasiya** is an aspiring software developer focused on learning and building web applications with Django, and maintains this project as an educational application.

- GitHub: [amreshchaurasiyatechedu](https://github.com/amreshchaurasiyatechedu)
- LinkedIn: [amreshchaurasiya](https://www.linkedin.com/in/amresh-chaurasiya)
- Email: [amreshchaurasiya__@gmail.com](mailto:amreshchaurasiya__@gmail.com)
- Project: [Django Student Management System](https://github.com/amreshchaurasiyatechedu/student-management-system)
