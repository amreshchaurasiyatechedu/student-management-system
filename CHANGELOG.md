# Changelog

Notable project changes are recorded here. Work that has not been published as
a release remains under **Unreleased**.

## Unreleased

### Added

- Branded, responsive dashboards and navigation for HOD, staff, and student
  roles, plus a public About/Credits page.
- Administrative student search and filters, and named academic sessions with
  a JSON management API.
- Maintenance and contribution documentation for ongoing development.
- Role-aware profile photos and profile directories for HOD, staff, and students.
- Clickable 48px sidebar profile links, local photo previews, and HOD photo
  management on authorized student/staff profile pages.

### Improved

- Environment-based Django secret, debug, and host configuration.
- CSRF protection and role-scoped validation for attendance and result
  workflows.
- Regression tests for authentication, role boundaries, attendance, results,
  academic sessions, student search, and profile photo access.
- Validated student profile photo uploads use private, role-checked delivery.
- The project README, setup instructions, and project attribution.

### Database

- Added a forward migration to align the custom user's first-name field with
  the current Django model while retaining the existing `AutoField` primary
  key type.
- Added an optional profile photo to the custom user model without removing
  the legacy student photo field.
