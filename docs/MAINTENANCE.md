# Project provenance and maintenance

## Project and maintainer

**Amresh Chaurasiya** maintains the Amresh Student Management System:

- GitHub: <https://github.com/amreshchaurasiyatechedu>
- Maintainer repository: <https://github.com/amreshchaurasiyatechedu/student-management-system>

The project is based on the [Django Student Management System by Vijay
Thapa](https://github.com/vijaythapa333/django-student-management-system).
This attribution does not claim or grant a license or other permission.

## Original components retained

The existing application remains a Django project with the
`student_management_app` application, a custom user model and HOD/staff/student
roles, separate role-specific views and templates, SQLite persistence, and
existing student, course, subject, attendance, results, leave, and feedback
workflows.

The UI continues to use the project's bundled AdminLTE, Bootstrap, and other
front-end assets. Preserve their existing license and notice files under
`static/`, along with required attribution in application credits.

## Maintainer contributions in this checkout

The maintained application adds or improves:

- Amresh branding, responsive role dashboards, navigation, and the public
  About/Credits page.
- Academic session naming and management, plus administrative student search
  and filtering.
- Environment-based Django security settings and CSRF-protected, role-scoped
  attendance and result workflows.
- Validation and regression coverage for authentication, role boundaries,
  attendance, results, and academic session behavior.
- Project setup, architecture, contribution, changelog, and maintenance
  documentation.

These are application changes, not a claim that the project is licensed for
production or redistribution.

## Ongoing maintenance responsibilities

- Keep `DJANGO_SECRET_KEY` private, keep `DJANGO_DEBUG` disabled outside local
  development, and set `DJANGO_ALLOWED_HOSTS` to deployment hostnames.
- Preserve student privacy. Use synthetic data for demonstrations, tests, and
  screenshots.
- Review role access and input validation when changing views, forms, or
  routes; test HOD, staff, and student workflows.
- Run the checks documented in [CONTRIBUTING.md](../CONTRIBUTING.md), review
  migration plans, and use new forward migrations rather than rewriting
  migrations that may already be applied.
- Record user-visible changes in [CHANGELOG.md](../CHANGELOG.md) and keep the
  README, setup instructions, and screenshots accurate.
- Retain project attribution and vendor notices. The repository currently has
  no root-level `LICENSE`; do not infer a license from the upstream project.

## Repository operations

At the time of this maintenance review, the local Git `origin` points to the
original upstream repository, while the maintainer repository is
`amreshchauriyasatechedu/student-management-system`. Confirm `git remote -v`
and the target repository before pushing; do not push this checkout to the
upstream project by mistake.

The repository currently has no `.github/` automation. Do not describe checks
as CI-enforced until a workflow is added and verified.
