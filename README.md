<div align="center">
  <h1>Amresh SMS</h1>
  <p><strong>Student Management System</strong></p>
  <p>A Django web application for managing student records and everyday academic workflows through role-specific dashboards.</p>
  <p>
    <a href="https://github.com/amreshchaurasiyatechedu/student-management-system">Project repository</a>
    ·
    <a href="https://www.youtube.com/watch?v=kArCR96m7uo">Video demonstration</a>
    ·
    <a href="#installation-and-setup">Get started</a>
  </p>
</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/status-maintained-2563EB)](https://github.com/amreshchaurasiyatechedu/student-management-system)
[![GitHub stars](https://img.shields.io/github/stars/amreshchaurasiyatechedu/student-management-system?style=social)](https://github.com/amreshchaurasiyatechedu/student-management-system)
[![GitHub forks](https://img.shields.io/github/forks/amreshchaurasiyatechedu/student-management-system?style=social)](https://github.com/amreshchaurasiyatechedu/student-management-system/forks)
[![GitHub issues](https://img.shields.io/github/issues/amreshchaurasiyatechedu/student-management-system)](https://github.com/amreshchaurasiyatechedu/student-management-system/issues)

</div>

**Maintained by [Amresh Chaurasiya](https://github.com/amreshchaurasiyatechedu)** · Application version **1.0**

> An educational project and ongoing maintainer effort. Python 3.13 was used in prior validation; this repository does not declare a minimum supported Python version.

### Quick navigation

[Features](#key-features) · [Screenshots](#application-screenshots) · [Technology](#technology-stack) · [Architecture](#project-architecture) · [Setup](#installation-and-setup) · [Contributing](#contributing-guidelines)

## Table of contents

1. [About the Project](#about-the-project)
2. [Key Features](#key-features)
3. [Application Screenshots](#application-screenshots)
4. [Live Demo and Video Demonstration](#live-demo-and-video-demonstration)
5. [Technology Stack](#technology-stack)
6. [User Roles and Permissions](#user-roles-and-permissions)
7. [Project Architecture](#project-architecture)
8. [Project Folder Structure](#project-folder-structure)
9. [Installation and Setup](#installation-and-setup)
10. [Environment Configuration](#environment-configuration)
11. [Database Configuration](#database-configuration)
12. [How to Use](#how-to-use)
13. [Security Features](#security-features)
14. [Project Roadmap](#project-roadmap)
15. [Future Enhancements](#future-enhancements)
16. [Contributing Guidelines](#contributing-guidelines)
17. [License and Original Attribution](#license-and-original-attribution)
18. [Frequently Asked Questions](#frequently-asked-questions)
19. [About the Developer](#about-the-developer)
20. [Contact and Support](#contact-and-support)

## About the Project

Amresh SMS brings common student and academic administration tasks into one Django application. HODs can manage users and academic records, staff can record attendance and marks, and students can review their own attendance and results.

The project began as a Django learning project and is maintained as an educational application. It can be explored as a learning resource or adapted as a starting point for institution-specific needs. Review and adapt the application before using it with real student data.

## Key Features

### HOD / Administrator

- View a dashboard with summary information and charts.
- Manage staff, students, courses, subjects, and academic sessions.
- Search and filter student records.
- Review attendance by subject and academic session.
- Review and reply to student and staff feedback.
- Approve or reject student and staff leave requests.
- Use the authorized user directory and manage profile photos.

### Staff / Teachers

- View a role-specific dashboard and teaching summaries.
- Take and update attendance for assigned subjects.
- Record and update student exam and assignment marks.
- Apply for leave and review application status.
- Send feedback to the HOD and view replies.
- Manage a personal profile and view students in assigned courses.

### Students

- View a personal dashboard with attendance summaries.
- Review attendance for subjects in their course.
- View recorded exam and assignment results.
- Apply for leave and review application status.
- Send feedback to the HOD and view replies.
- Manage a personal profile and profile photo.

## Application Screenshots

The repository does not currently contain authenticated dashboard captures. The running site was available at its sign-in page, but the browser session did not have access to HOD, staff, or student dashboards. No synthetic or unrelated screenshots are used here.

The Admin / HOD dashboard is intended to be the lead image in this gallery. Please add authentic captures to `screenshots/` using these filenames; image links will be added once the real files are available.

| Screen | File to provide | Status |
| --- | --- | --- |
| Admin / HOD dashboard | `screenshots/admin-dashboard.png` | Awaiting authentic capture |
| Staff / Teacher dashboard | `screenshots/teacher-dashboard.png` | Awaiting authentic capture |
| Student dashboard | `screenshots/student-dashboard.png` | Awaiting authentic capture |
| Attendance management | `screenshots/attendance-management.png` | Awaiting authentic capture |
| Results management | `screenshots/results-management.png` | Awaiting authentic capture |
| Student management | `screenshots/student-management.png` | Awaiting authentic capture |

Use demonstration data only. Remove or obscure personal information before sharing captures publicly.

## Live Demo and Video Demonstration

Watch the existing [Amresh SMS project demonstration on YouTube](https://www.youtube.com/watch?v=kArCR96m7uo).

The video is linked as text only; this README intentionally does not embed a YouTube thumbnail.

## Technology Stack

### Backend

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)

- Python is the application language.
- Django 6.1.2 is pinned in [`requirements.txt`](requirements.txt).
- Django templates and the ORM power server-rendered pages and data access.

### Frontend

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-4-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![AdminLTE](https://img.shields.io/badge/AdminLTE-3-3C8DBC)](https://adminlte.io/)
[![jQuery](https://img.shields.io/badge/jQuery-0769AD?logo=jquery&logoColor=white)](https://jquery.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

The interface uses HTML templates, CSS, JavaScript, bundled Bootstrap and AdminLTE assets, jQuery, and Chart.js.

### Database

[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

SQLite is the database configured by the Django settings. Although `mysql-connector-python` appears in the dependency file, this project does not configure MySQL as a Django database backend.

### Libraries and dependencies

The pinned Python dependencies in [`requirements.txt`](requirements.txt) are:

`asgiref`, `Django`, `django-extensions`, `graphviz`, `mysql-connector-python`, `Pillow`, `protobuf`, `pydot`, `pyparsing`, `pytz`, `six`, `sqlparse`, and `tzdata`.

### Development tools

- Python and pip for the virtual environment and package installation.
- Git for source control.
- Django management commands for migrations, checks, the development server, and tests.

## User Roles and Permissions

| Role | Main responsibilities |
| --- | --- |
| HOD / Administrator | Manage academic records and users, review attendance, feedback, and leave, and access the authorized user directory. |
| Staff / Teacher | Manage attendance and results for assigned teaching work, and access permitted student profiles associated with their courses. |
| Student | View and manage personal profile information, attendance, results, leave requests, and feedback. |

The application uses a custom Django user model with HOD, Staff, and Student roles. Profile and directory views enforce role-specific access on the server; students do not have access to the user directory, and staff access to students is restricted to their assignments.

## Project Architecture

- **`student_management_system`** is the Django project package. Its settings configure the installed app, custom user model, SQLite database, authentication, templates, and static/media paths.
- **`student_management_app`** contains the application models, migrations, forms, URL routes, views, validators, authentication backend, and tests.
- **Role-specific view modules** separate HOD, staff, and student workflows. Templates are grouped by role, with shared profile templates under `profiles/`.
- **Django ORM models** represent users and role profiles, courses, subjects, academic sessions, attendance, results, leave, feedback, and notifications.
- The application includes JSON endpoints for academic session data. Other workflows are served through Django views and templates.

The principal dashboard templates are `hod_template/home_content.html`, `staff_template/staff_home_template.html`, and `student_template/student_home_template.html`. The main workflow templates include `hod_template/manage_student_template.html`, `hod_template/admin_view_attendance.html`, `staff_template/take_attendance_template.html`, `staff_template/add_result_template.html`, and `student_template/student_view_result.html`.

## Project Folder Structure

```text
.
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docs/
│   └── MAINTENANCE.md
├── manage.py
├── requirements.txt
├── screenshots/                    # Genuine app captures; requested images are pending
├── static/                         # Bundled CSS, JavaScript, fonts, and vendor assets
├── student_management_app/
│   ├── migrations/
│   ├── templates/
│   │   ├── hod_template/
│   │   ├── profiles/
│   │   ├── staff_template/
│   │   └── student_template/
│   ├── HodViews.py
│   ├── EmailBackEnd.py
│   ├── LoginCheckMiddleWare.py
│   ├── ProfileViews.py
│   ├── StaffViews.py
│   ├── StudentViews.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   ├── validators.py
│   └── views.py
└── student_management_system/
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

Local databases, uploaded media, environment files, and generated files are excluded from the published project.

## Installation and Setup

### Prerequisites

- Git.
- Python with `venv` and pip. Python 3.13 was used in prior validation; this repository does not declare a minimum supported Python version.

### Clone the repository

```bash
git clone https://github.com/amreshchaurasiyatechedu/student-management-system.git
cd student-management-system
```

### Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure the environment

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS` as described in [Environment Configuration](#environment-configuration). For local development, use `127.0.0.1,localhost` for allowed hosts.

### Apply migrations and create an administrator

```bash
python manage.py migrate
python manage.py createsuperuser
```

The custom user model defaults a new superuser to the HOD role. Use the email address and password you set when prompted to sign in.

### Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser. The Django admin site is available at `/admin/`.

## Environment Configuration

The project reads configuration from process environment variables. There is no `.env` loader, so a `.env` file alone will not configure the application.

| Variable | Required | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Yes | Django signing key. The application raises a configuration error if it is missing or blank. |
| `DJANGO_DEBUG` | No | Enables debug mode only for recognized true values; defaults to `false`. |
| `DJANGO_ALLOWED_HOSTS` | No | Comma-separated hostnames; defaults to an empty list. The wildcard `*` is rejected. |

Set the variables in the same terminal session used to run Django.

**Windows PowerShell**

```powershell
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
```

**Windows Command Prompt**

```bat
for /f %i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set "DJANGO_SECRET_KEY=%i"
set "DJANGO_DEBUG=true"
set "DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost"
```

**macOS / Linux**

```bash
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

For production, keep debug mode disabled and set the exact hostnames used by the deployment. Never commit secret values.

## Database Configuration

SQLite is the database backend configured in `student_management_system/settings.py`. The local database path is `db.sqlite3` in the project root. No database server or database credentials are required for local development.

Create the database and apply app and Django migrations with:

```bash
python manage.py migrate
```

The main models include:

- `CustomUser`, with one-to-one HOD, staff, and student role profiles.
- `Courses` and `Subjects`, with subjects assigned to a course and staff user.
- `SessionYearModel`, referenced by students and attendance records.
- `Attendance` and `AttendanceReport`, recording subject attendance and each student's status.
- `StudentResult`, linking students and subjects with exam and assignment marks.
- Student and staff leave, feedback, and notification records.

`mysql-connector-python` is listed as a dependency, but MySQL is not configured in Django settings.

## How to Use

1. Install dependencies, configure the environment variables, and run migrations.
2. Create an HOD account with `python manage.py createsuperuser`.
3. Sign in at `/` using the account's email and password.
4. Use the HOD dashboard to create courses, academic sessions, subjects, staff, and students.
5. Sign in with staff accounts to record attendance, enter results, and submit leave or feedback.
6. Sign in with student accounts to review attendance and results and use leave or feedback workflows.
7. Users can manage their own profile and profile photo from their profile page. Directory and profile access depends on role and teaching assignments.

No shared demo accounts or passwords are provided. Use synthetic records for demonstrations.

## Security Features

- Django's CSRF middleware is enabled; state-changing forms and AJAX workflows use CSRF protection.
- The app uses Django password validation and email-based authentication.
- Profile photo uploads are validated for supported image content and file size.
- Profile and directory requests use server-side, role-aware access checks. Profile photos are delivered through application views rather than relying on hidden UI links.
- `DJANGO_SECRET_KEY` is required; `DJANGO_DEBUG` defaults to false; unrestricted wildcard hosts are rejected.
- `.gitignore` excludes local environment files, databases, and uploaded media.

This project is intended for development and education and is not production-hardened. For deployment, use HTTPS, secure cookie settings, a private secret store, exact allowed hosts, and the [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/). Do not serve the profile-photo storage directory directly from a public web server or object-storage bucket.

## Project Roadmap

### Implemented

- Role-specific HOD, staff, and student dashboards.
- Management of staff, students, courses, subjects, and academic sessions.
- Student search and filtering.
- Attendance recording, updates, and student attendance views.
- Exam and assignment result management.
- Leave submission and HOD review.
- Feedback submission and HOD replies.
- Email-based login and role-specific routing.
- Validated profile photos and role-scoped profile views and directories.

## Future Enhancements

The following are potential improvements, not features currently available:

- Email notifications for academic and account events.
- More advanced dashboard analytics and reports.
- PDF or Excel exports for attendance and results.
- Further responsive UI refinements.
- Broader API coverage for application workflows.
- More granular permissions and expanded role-specific authorization testing.

## Contributing Guidelines

Contributions and focused improvements are welcome:

1. Fork the repository.
2. Create a feature branch from `main`.
3. Make a focused change and add or update relevant tests.
4. Run `python manage.py check` and `python manage.py test student_management_app`.
5. Commit your changes and open a pull request with a clear description.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the project workflow. Do not include credentials, local database files, uploaded media, or real student information.

## License and Original Attribution

No root-level `LICENSE` file is present in this repository, so licensing information has not been specified. Do not assume that a license is granted.

This project is based on the [Django Student Management System by Vijay Thapa](https://github.com/vijaythapa333/django-student-management-system). Amresh Chaurasiya maintains this repository and has added the branding, documentation, profile management, validation, and other improvements described in [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md). This attribution does not claim inherited work as wholly original or grant additional rights.

Retain the original application credits and bundled third-party license or notice files when modifying or redistributing those assets.

## Frequently Asked Questions

<details>
  <summary>Which database does the application use?</summary>

  SQLite is configured by default. The presence of `mysql-connector-python` in `requirements.txt` does not mean MySQL is configured.
</details>

<details>
  <summary>Where do I set the secret key?</summary>

  Set `DJANGO_SECRET_KEY` in the environment of the terminal running Django. This project does not load a `.env` file.
</details>

<details>
  <summary>How do I create an administrator account?</summary>

  Run `python manage.py createsuperuser`. The custom user model defaults the account to the HOD role.
</details>

<details>
  <summary>Are demo usernames and passwords available?</summary>

  No. Create your own account and use synthetic data for demonstrations.
</details>

<details>
  <summary>Where should I place screenshots?</summary>

  Add genuine, privacy-safe captures to `screenshots/` using the filenames in the [Application Screenshots](#application-screenshots) table. Do not include real student data.
</details>

## About the Developer

**Amresh Chaurasiya** is the project maintainer.

> Student Developer | Python and Django Enthusiast | Aspiring Software Developer

The repository does not currently contain a verified portrait of the maintainer. The intended asset location is `screenshots/amresh-chaurasiya.png`; it will be embedded only after Amresh provides the photograph. No stock, tutorial-creator, or generated portrait is used.

## Contact and Support

- **GitHub:** [amreshchaurasiyatechedu](https://github.com/amreshchaurasiyatechedu)
- **LinkedIn:** [Amresh Chaurasiya](https://www.linkedin.com/in/amresh-chaurasiya)
- **Email:** [amreshchaurasiya__@gmail.com](mailto:amreshchaurasiya__@gmail.com)
- **Project issues:** [Open an issue](https://github.com/amreshchaurasiyatechedu/student-management-system/issues)
