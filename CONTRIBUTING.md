# Contributing

Contributions that preserve the existing Django application and its role-based
workflows are welcome.

## Development setup

Follow the [README installation guide](README.md#installation-and-setup) to
create a virtual environment, install dependencies, and configure the required
environment variables.

Before submitting a change, run:

```bash
python manage.py check
python manage.py test student_management_app
python manage.py makemigrations --check --dry-run
```

If a change requires a schema update, create a new forward migration and review
it before applying it. Do not edit migrations that may already have been
applied.

## Pull request workflow

1. Fork the maintainer repository and create a focused branch.
2. Make the smallest change that addresses the issue and add tests for changed
   behavior.
3. Update the README or changelog when user-facing behavior or setup changes.
4. Open a pull request describing the change, its impact on HOD, staff, and
   student workflows, and the checks you ran.

## Project and data safeguards

- Keep secrets, local databases, uploaded files, and real student information
  out of commits, test fixtures, and screenshots.
- Preserve the original project attribution and all third-party license or
  notice files bundled under `static/`.
- The repository has no root-level project license at present. Do not add a
  license claim or assume permission to redistribute upstream material.
