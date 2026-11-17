from django.test import TestCase
from django.urls import reverse
import json

from django.utils.dateparse import parse_date

from .models import Attendance, Courses, CustomUser, SessionYearModel, Students, Subjects


class SessionYearApiTests(TestCase):
    def setUp(self):
        self.hod = CustomUser.objects.create_user(
            username="session-admin",
            password="test-password",
            user_type="1",
        )
        self.client.force_login(self.hod)
        self.sessions_url = reverse("session_years_api")

    def test_creates_session_with_custom_name_and_arbitrary_dates(self):
        response = self.client.post(self.sessions_url, {
            "session_name": "Custom Academic Year",
            "session_start_year": "2055-08-14",
            "session_end_year": "2056-05-30",
        })

        self.assertEqual(response.status_code, 201)
        session = SessionYearModel.objects.get()
        self.assertEqual(session.session_name, "Custom Academic Year")
        self.assertEqual(session.session_start_year.isoformat(), "2055-08-14")
        self.assertEqual(response.json()["session"]["display_name"], "Custom Academic Year")

    def test_rejects_invalid_and_duplicate_date_ranges(self):
        invalid_response = self.client.post(self.sessions_url, {
            "session_start_year": "2055-08-14",
            "session_end_year": "2055-08-13",
        })
        self.assertEqual(invalid_response.status_code, 400)

        SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        duplicate_response = self.client.post(self.sessions_url, {
            "session_start_year": "2055-08-14",
            "session_end_year": "2056-05-30",
        })
        self.assertEqual(duplicate_response.status_code, 400)

    def test_lists_updates_and_deletes_sessions(self):
        session = SessionYearModel.objects.create(
            session_name="Before",
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        list_response = self.client.get(self.sessions_url)
        self.assertEqual(list_response.json()["sessions"][0]["display_name"], "Before")

        update_response = self.client.patch(
            reverse("session_year_api", args=[session.id]),
            data='{"session_name":"After"}',
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        session.refresh_from_db()
        self.assertEqual(session.session_name, "After")

        delete_response = self.client.delete(reverse("session_year_api", args=[session.id]))
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(SessionYearModel.objects.filter(id=session.id).exists())

    def test_attendance_page_renders_dynamic_sessions_and_management_controls(self):
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )

        response = self.client.get(reverse("admin_view_attendance"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, session.display_name)
        self.assertContains(response, "+ Add Session Year")
        self.assertContains(response, "Manage Sessions")

    def test_prevents_deleting_session_with_student_data(self):
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        course = Courses.objects.create(course_name="Test course")
        student_user = CustomUser.objects.create_user(
            username="session-student",
            password="test-password",
            user_type="4",
        )
        student = Students.objects.create(
            admin=student_user,
            gender="",
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )

        response = self.client.delete(reverse("session_year_api", args=[session.id]))

        self.assertEqual(response.status_code, 409)
        self.assertTrue(SessionYearModel.objects.filter(id=session.id).exists())
        self.assertTrue(Students.objects.filter(id=student.id).exists())

    def test_edit_cannot_move_existing_attendance_outside_session(self):
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        course = Courses.objects.create(course_name="Protected attendance course")
        subject = Subjects.objects.create(
            subject_name="Protected attendance subject",
            course_id=course,
            staff_id=self.hod,
        )
        attendance = Attendance.objects.create(
            subject_id=subject,
            session_year_id=session,
            attendance_date=parse_date("2055-09-01"),
        )

        response = self.client.patch(
            reverse("session_year_api", args=[session.id]),
            data='{"session_start_year":"2055-09-02"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(Attendance.objects.filter(id=attendance.id).exists())

    def test_attendance_dates_are_limited_to_selected_session_range(self):
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        course = Courses.objects.create(course_name="Attendance course")
        subject = Subjects.objects.create(
            subject_name="Attendance subject",
            course_id=course,
            staff_id=self.hod,
        )
        in_range = Attendance.objects.create(
            subject_id=subject,
            session_year_id=session,
            attendance_date=parse_date("2055-09-01"),
        )
        Attendance.objects.create(
            subject_id=subject,
            session_year_id=session,
            attendance_date=parse_date("2056-06-01"),
        )

        response = self.client.post(reverse("admin_get_attendance_dates"), {
            "subject": subject.id,
            "session_year_id": session.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual([entry["id"] for entry in response.json()], [in_range.id])

    def test_attendance_save_accepts_only_dates_inside_selected_session(self):
        staff = CustomUser.objects.create_user(
            username="attendance-staff",
            password="test-password",
            user_type="2",
        )
        self.client.force_login(staff)
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        course = Courses.objects.create(course_name="Take attendance course")
        subject = Subjects.objects.create(
            subject_name="Take attendance subject",
            course_id=course,
            staff_id=staff,
        )
        student_user = CustomUser.objects.create_user(
            username="attendance-student",
            password="test-password",
            user_type="4",
        )
        student = Students.objects.create(
            admin=student_user,
            gender="",
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )
        payload = {
            "student_ids": json.dumps([{"id": student_user.id, "status": 1}]),
            "subject_id": subject.id,
            "session_year_id": session.id,
        }

        invalid_response = self.client.post(
            reverse("save_attendance_data"),
            {**payload, "attendance_date": "2056-06-01"},
        )
        self.assertEqual(invalid_response.status_code, 400)
        self.assertFalse(Attendance.objects.filter(session_year_id=session).exists())

        valid_response = self.client.post(
            reverse("save_attendance_data"),
            {**payload, "attendance_date": "2055-09-01"},
        )
        self.assertEqual(valid_response.status_code, 200)
        self.assertTrue(Attendance.objects.filter(
            session_year_id=session,
            attendance_date=parse_date("2055-09-01"),
        ).exists())
