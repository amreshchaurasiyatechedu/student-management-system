from io import BytesIO

from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from django.utils.dateparse import parse_date
from django.test import override_settings
from PIL import Image

from .models import (
    Attendance,
    AttendanceReport,
    Courses,
    CustomUser,
    SessionYearModel,
    Staffs,
    StudentResult,
    Students,
    Subjects,
)
from .validators import MAX_PROFILE_PHOTO_SIZE, validate_profile_photo


class BrandingPageTests(TestCase):
    def test_login_page_has_custom_branding_and_accessible_sign_in_fields(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amresh Student Management System")
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'autocomplete="current-password"')
        self.assertContains(response, reverse("about"))

    def test_about_page_is_available_without_authentication(self):
        response = self.client.get(reverse("about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amresh Chaurasiya")
        self.assertContains(response, "AdminLTE 3.0.5")

    def test_role_dashboards_render_the_personalized_branding(self):
        course = Courses.objects.create(course_name="Branding test course")
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        admin = CustomUser.objects.create_user(
            username="branding-admin",
            password="test-password",
            first_name="Alex",
            user_type="1",
        )
        staff = CustomUser.objects.create_user(
            username="branding-staff",
            password="test-password",
            first_name="Sam",
            user_type="2",
        )
        student = CustomUser.objects.create_user(
            username="branding-student",
            password="test-password",
            first_name="Taylor",
            user_type="3",
        )
        Staffs.objects.create(admin=staff, address="")
        Students.objects.create(
            admin=student,
            gender="",
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )

        dashboards = (
            (admin, "admin_home", "Alex"),
            (staff, "staff_home", "Sam"),
            (student, "student_home", "Taylor"),
        )
        for user, route_name, first_name in dashboards:
            with self.subTest(role=user.user_type):
                self.client.force_login(user)
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Amresh Student Management System")
                self.assertContains(response, f"Welcome back, {first_name}")
                self.assertContains(response, reverse("about"))


class AuthenticationWorkflowTests(TestCase):
    def test_login_form_enforces_csrf_and_authenticated_users_leave_the_login_page(self):
        admin = CustomUser.objects.create_user(
            username="csrf-login-admin",
            email="csrf-admin@example.test",
            password="strong-test-password",
            user_type="1",
        )
        csrf_client = Client(enforce_csrf_checks=True)

        login_page = csrf_client.get(reverse("login"))
        self.assertEqual(login_page.status_code, 200)
        self.assertIn("no-store", login_page["Cache-Control"])
        csrf_token = csrf_client.cookies["csrftoken"].value

        login_response = csrf_client.post(reverse("doLogin"), {
            "email": admin.email,
            "password": "strong-test-password",
            "csrfmiddlewaretoken": csrf_token,
        })
        self.assertRedirects(
            login_response,
            reverse("admin_home"),
            fetch_redirect_response=False,
        )

        stale_login_page_response = csrf_client.get(reverse("login"))
        self.assertRedirects(
            stale_login_page_response,
            reverse("admin_home"),
            fetch_redirect_response=False,
        )

    def test_users_can_sign_in_by_email_and_invalid_credentials_are_rejected(self):
        admin = CustomUser.objects.create_user(
            username="authentication-admin",
            email="admin@example.test",
            password="strong-test-password",
            user_type="1",
        )

        valid_response = self.client.post(reverse("doLogin"), {
            "email": admin.email,
            "password": "strong-test-password",
        })
        self.assertRedirects(
            valid_response,
            reverse("admin_home"),
            fetch_redirect_response=False,
        )

        self.client.logout()
        invalid_response = self.client.post(reverse("doLogin"), {
            "email": admin.email,
            "password": "incorrect-password",
        })
        self.assertRedirects(
            invalid_response,
            reverse("login"),
            fetch_redirect_response=False,
        )

    def test_students_only_see_their_own_results(self):
        course = Courses.objects.create(course_name="Results course")
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        subject = Subjects.objects.create(
            subject_name="Visible subject",
            course_id=course,
            staff_id=CustomUser.objects.create_user(
                username="results-staff",
                password="test-password",
                user_type="2",
            ),
        )
        student_user = CustomUser.objects.create_user(
            username="results-student",
            password="test-password",
            user_type="3",
        )
        other_user = CustomUser.objects.create_user(
            username="other-results-student",
            password="test-password",
            user_type="3",
        )
        student = Students.objects.create(
            admin=student_user,
            gender="",
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )
        other_student = Students.objects.create(
            admin=other_user,
            gender="",
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )
        StudentResult.objects.create(
            student_id=student,
            subject_id=subject,
            subject_exam_marks=87,
            subject_assignment_marks=92,
        )
        StudentResult.objects.create(
            student_id=other_student,
            subject_id=subject,
            subject_exam_marks=12,
            subject_assignment_marks=15,
        )

        self.client.force_login(student_user)
        response = self.client.get(reverse("student_view_result"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visible subject")
        self.assertContains(response, "87.0")
        self.assertNotContains(response, "12.0")


class ProfilePhotoAccessTests(TestCase):
    def setUp(self):
        media_settings = override_settings(STORAGES={
            "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        })
        media_settings.enable()
        self.addCleanup(media_settings.disable)

        self.course = Courses.objects.create(course_name="Profile Course")
        self.other_course = Courses.objects.create(course_name="Other Course")
        self.session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        self.other_session = SessionYearModel.objects.create(
            session_start_year=parse_date("2056-08-14"),
            session_end_year=parse_date("2057-05-30"),
        )
        self.hod = CustomUser.objects.create_user(
            username="profile-hod",
            password="test-password",
            first_name="Hall",
            last_name="Administrator",
            user_type=1,
        )
        self.staff = CustomUser.objects.create_user(
            username="profile-staff",
            password="test-password",
            first_name="Terry",
            last_name="Teacher",
            user_type=2,
        )
        self.other_staff = CustomUser.objects.create_user(
            username="other-profile-staff",
            password="test-password",
            first_name="Other",
            last_name="Teacher",
            user_type=2,
        )
        self.assigned_student = self._create_student(
            "assigned-profile-student",
            "Avery",
            "Learner",
            self.course,
            self.session,
        )
        self.unassigned_student = self._create_student(
            "unassigned-profile-student",
            "Morgan",
            "Learner",
            self.other_course,
            self.other_session,
        )
        self.subject = Subjects.objects.create(
            subject_name="Assigned Subject",
            course_id=self.course,
            staff_id=self.staff,
        )
        Subjects.objects.create(
            subject_name="Other Subject",
            course_id=self.other_course,
            staff_id=self.other_staff,
        )

    def _create_student(self, username, first_name, last_name, course, session):
        user = CustomUser.objects.create_user(
            username=username,
            password="test-password",
            first_name=first_name,
            last_name=last_name,
            user_type=3,
        )
        student = user.students
        student.course_id = course
        student.session_year_id = session
        student.save()
        return user

    @staticmethod
    def _image(name="avatar.png", color="blue"):
        image_bytes = BytesIO()
        Image.new("RGB", (8, 8), color=color).save(image_bytes, format="PNG")
        return SimpleUploadedFile(
            name,
            image_bytes.getvalue(),
            content_type="image/png",
        )

    def _add_photo(self, user, name="seed.png"):
        user.profile_photo.save(name, self._image(name), save=True)
        return user.profile_photo.name

    def test_all_roles_can_upload_replace_and_remove_their_own_photo(self):
        user_roles = (
            (self.hod, "admin_home", "admin_profile"),
            (self.staff, "staff_home", "staff_profile"),
            (self.assigned_student, "student_home", "student_profile"),
        )
        client = Client()

        for user, dashboard_name, existing_profile_name in user_roles:
            with self.subTest(role=user.user_type):
                client.force_login(user)
                upload_response = client.post(
                    reverse("my_profile"),
                    {"profile_photo": self._image()},
                )
                self.assertRedirects(
                    upload_response,
                    reverse("my_profile"),
                    fetch_redirect_response=False,
                )
                user.refresh_from_db()
                old_name = user.profile_photo.name
                photo_response = client.get(
                    reverse("profile_photo", kwargs={"user_id": user.pk}),
                )
                self.assertEqual(photo_response.status_code, 200)
                self.assertEqual(photo_response["Content-Type"], "image/png")
                self.assertEqual(photo_response["X-Content-Type-Options"], "nosniff")
                photo_response.close()

                profile_response = client.get(reverse("my_profile"))
                self.assertContains(
                    profile_response,
                    reverse("profile_photo", kwargs={"user_id": user.pk}),
                )
                dashboard_response = client.get(reverse(dashboard_name))
                self.assertContains(
                    dashboard_response,
                    reverse("profile_photo", kwargs={"user_id": user.pk}),
                )
                existing_profile_response = client.get(reverse(existing_profile_name))
                self.assertContains(
                    existing_profile_response,
                    reverse("profile_photo", kwargs={"user_id": user.pk}),
                )

                replacement_response = client.post(
                    reverse("my_profile"),
                    {"profile_photo": self._image(color="red")},
                )
                self.assertRedirects(
                    replacement_response,
                    reverse("my_profile"),
                    fetch_redirect_response=False,
                )
                user.refresh_from_db()
                self.assertNotEqual(user.profile_photo.name, old_name)
                self.assertFalse(user.profile_photo.storage.exists(old_name))

                replacement_name = user.profile_photo.name
                remove_response = client.post(
                    reverse("my_profile"),
                    {"clear_photo": "on"},
                )
                self.assertRedirects(
                    remove_response,
                    reverse("my_profile"),
                    fetch_redirect_response=False,
                )
                user.refresh_from_db()
                self.assertFalse(user.profile_photo)
                self.assertFalse(user.profile_photo.storage.exists(replacement_name))
                client.logout()

    def test_sidebar_profile_section_links_to_profile_with_initial_avatar(self):
        user_roles = (
            (self.hod, "admin_home"),
            (self.staff, "staff_home"),
            (self.assigned_student, "student_home"),
        )
        client = Client()

        for user, dashboard_name in user_roles:
            with self.subTest(role=user.user_type):
                client.force_login(user)
                response = client.get(reverse(dashboard_name))
                self.assertContains(response, 'class="user-profile-link"')
                self.assertContains(
                    response,
                    f'href="{reverse("my_profile")}" class="user-profile-link"',
                )
                self.assertContains(response, "profile-avatar sidebar-avatar")
                self.assertContains(response, user.avatar_initials)
                client.logout()

    def test_profile_page_includes_local_image_preview_control(self):
        self._add_photo(self.hod)
        self.client.force_login(self.hod)

        response = self.client.get(reverse("my_profile"))

        self.assertContains(response, 'id="profile-photo-preview"')
        self.assertContains(response, "URL.createObjectURL(file)")
        self.assertContains(response, "Change photo")
        self.assertContains(response, "Remove photo", html=False)

    def test_profile_photo_and_directory_views_require_authentication(self):
        protected_urls = (
            reverse("my_profile"),
            reverse("user_directory"),
            reverse("staff_student_directory"),
            reverse("profile_detail", kwargs={"user_id": self.assigned_student.pk}),
            reverse("profile_photo", kwargs={"user_id": self.assigned_student.pk}),
        )

        for url in protected_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_hod_can_manage_student_and_staff_photos_from_authorized_profiles(self):
        self.client.force_login(self.hod)

        for target in (self.assigned_student, self.staff):
            with self.subTest(target=target.username):
                old_name = self._add_photo(target, name="old.png")
                profile_url = reverse("profile_detail", kwargs={"user_id": target.pk})
                profile_response = self.client.get(profile_url)
                self.assertContains(profile_response, 'id="id_profile_photo"')
                self.assertContains(profile_response, "Remove photo")

                update_response = self.client.post(
                    profile_url,
                    {"profile_photo": self._image(name="new.png", color="red")},
                )
                self.assertRedirects(
                    update_response,
                    profile_url,
                    fetch_redirect_response=False,
                )
                target.refresh_from_db()
                self.assertNotEqual(target.profile_photo.name, old_name)
                self.assertFalse(target.profile_photo.storage.exists(old_name))

                remove_response = self.client.post(
                    profile_url,
                    {"clear_photo": "on"},
                )
                self.assertRedirects(
                    remove_response,
                    profile_url,
                    fetch_redirect_response=False,
                )
                target.refresh_from_db()
                self.assertFalse(target.profile_photo)

    def test_students_cannot_access_other_roles_or_other_students(self):
        self.client.force_login(self.assigned_student)
        no_photo_profile = self.client.get(
            reverse("profile_detail", kwargs={"user_id": self.assigned_student.pk}),
        )
        self.assertContains(no_photo_profile, self.assigned_student.avatar_initials)
        assigned_photo = self._add_photo(self.assigned_student)
        other_photo = self._add_photo(self.unassigned_student)
        staff_photo = self._add_photo(self.staff)
        hod_photo = self._add_photo(self.hod)

        own_profile = self.client.get(
            reverse("profile_detail", kwargs={"user_id": self.assigned_student.pk}),
        )
        self.assertEqual(own_profile.status_code, 200)
        self.assertContains(
            own_profile,
            reverse("profile_photo", kwargs={"user_id": self.assigned_student.pk}),
        )
        own_photo_response = self.client.get(
            reverse("profile_photo", kwargs={"user_id": self.assigned_student.pk}),
        )
        self.assertEqual(own_photo_response.status_code, 200)
        own_photo_response.close()
        for other_user, photo_name in (
            (self.unassigned_student, other_photo),
            (self.staff, staff_photo),
            (self.hod, hod_photo),
        ):
            with self.subTest(target=other_user.username, photo=photo_name):
                self.assertEqual(
                    self.client.get(
                        reverse("profile_detail", kwargs={"user_id": other_user.pk}),
                    ).status_code,
                    404,
                )
                self.assertEqual(
                    self.client.get(
                        reverse("profile_photo", kwargs={"user_id": other_user.pk}),
                    ).status_code,
                    404,
                )
        self.assertTrue(self.assigned_student.profile_photo.storage.exists(assigned_photo))
        self.assertEqual(self.client.get(reverse("user_directory")).status_code, 404)

    def test_staff_can_view_only_students_in_their_assigned_courses(self):
        assigned_photo = self._add_photo(self.assigned_student)
        self._add_photo(self.unassigned_student)
        self._add_photo(self.hod)
        self.client.force_login(self.staff)

        response = self.client.get(reverse("staff_student_directory"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Avery Learner")
        self.assertNotContains(response, "Morgan Learner")

        assigned_profile = self.client.get(
            reverse("profile_detail", kwargs={"user_id": self.assigned_student.pk}),
        )
        self.assertEqual(assigned_profile.status_code, 200)
        self.assertContains(assigned_profile, "Assigned Subject")
        self.assertNotContains(assigned_profile, "Other Subject")
        assigned_photo_response = self.client.get(
            reverse("profile_photo", kwargs={"user_id": self.assigned_student.pk}),
        )
        self.assertEqual(assigned_photo_response.status_code, 200)
        assigned_photo_response.close()
        self.assertEqual(
            self.client.post(
                reverse("profile_detail", kwargs={"user_id": self.assigned_student.pk}),
                {"clear_photo": "on"},
            ).status_code,
            404,
        )
        self.assigned_student.refresh_from_db()
        self.assertEqual(self.assigned_student.profile_photo.name, assigned_photo)
        for protected_user in (self.unassigned_student, self.hod, self.other_staff):
            with self.subTest(target=protected_user.username):
                self.assertEqual(
                    self.client.get(
                        reverse("profile_detail", kwargs={"user_id": protected_user.pk}),
                    ).status_code,
                    404,
                )
                self.assertEqual(
                    self.client.get(
                        reverse("profile_photo", kwargs={"user_id": protected_user.pk}),
                    ).status_code,
                    404,
                )
        self.assertTrue(self.assigned_student.profile_photo.storage.exists(assigned_photo))
        self.assertEqual(self.client.get(reverse("user_directory")).status_code, 404)

    def test_hod_can_search_filter_and_open_student_and_staff_profiles(self):
        self._add_photo(self.assigned_student)
        self._add_photo(self.staff)
        CustomUser.objects.create_user(
            username="directory-instructor",
            password="test-password",
            first_name="Ada",
            last_name="Lovelace",
            user_type=2,
        )
        self.client.force_login(self.hod)
        teacher_search = self.client.get(reverse("user_directory"), {"q": "teacher"})
        self.assertEqual(teacher_search.status_code, 200)
        self.assertContains(teacher_search, "Ada Lovelace")
        self.assertNotContains(teacher_search, "Morgan Learner")

        response = self.client.get(
            reverse("user_directory"),
            {
                "q": str(self.assigned_student.students.pk),
                "role": "3",
                "course_id": str(self.course.pk),
                "subject_id": str(self.subject.pk),
                "session_year_id": str(self.session.pk),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Avery Learner")
        self.assertNotContains(response, "Morgan Learner")
        self.assertEqual(
            self.client.get(
                reverse("profile_detail", kwargs={"user_id": self.assigned_student.pk}),
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("profile_detail", kwargs={"user_id": self.staff.pk}),
            ).status_code,
            200,
        )
        staff_photo_response = self.client.get(
            reverse("profile_photo", kwargs={"user_id": self.staff.pk}),
        )
        self.assertEqual(staff_photo_response.status_code, 200)
        staff_photo_response.close()

    def test_hod_student_creation_saves_validated_photo_to_private_profile_storage(self):
        self.client.force_login(self.hod)
        response = self.client.post(
            reverse("add_student_save"),
            {
                "email": "new-profile-student@example.test",
                "password": "test-password",
                "first_name": "New",
                "last_name": "Student",
                "username": "new-profile-student",
                "address": "Campus",
                "course_id": str(self.course.pk),
                "gender": "Male",
                "session_year_id": str(self.session.pk),
                "profile_pic": self._image(),
            },
        )
        self.assertRedirects(
            response,
            reverse("add_student"),
            fetch_redirect_response=False,
        )
        student_user = CustomUser.objects.get(username="new-profile-student")
        self.assertTrue(student_user.profile_photo.name.startswith("profile_photos/"))
        photo_response = self.client.get(
            reverse("profile_photo", kwargs={"user_id": student_user.pk}),
        )
        self.assertEqual(photo_response.status_code, 200)
        photo_response.close()

    def test_profile_photos_are_not_served_directly_from_media_url(self):
        self._add_photo(self.assigned_student)
        self.client.force_login(self.hod)
        direct_media_url = f"{settings.MEDIA_URL}{self.assigned_student.profile_photo.name}"

        response = self.client.get(direct_media_url)

        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_legacy_student_media_photos_use_role_based_access(self):
        legacy_name = default_storage.save(
            "legacy-student.png",
            self._image(name="legacy-student.png"),
        )
        student = self.assigned_student.students
        student.profile_pic = legacy_name
        student.save(update_fields=["profile_pic"])
        legacy_url = f"{settings.MEDIA_URL}{legacy_name}"

        self.client.force_login(self.unassigned_student)
        self.assertEqual(self.client.get(legacy_url).status_code, 404)

        self.client.force_login(self.staff)
        staff_response = self.client.get(legacy_url)
        self.assertEqual(staff_response.status_code, 200)
        staff_response.close()

        self.client.force_login(self.hod)
        hod_response = self.client.get(legacy_url)
        self.assertEqual(hod_response.status_code, 200)
        hod_response.close()

    def test_photo_validator_rejects_bad_extensions_content_and_oversized_files(self):
        with self.assertRaises(ValidationError):
            validate_profile_photo(SimpleUploadedFile("avatar.svg", b"<svg></svg>"))
        with self.assertRaises(ValidationError):
            validate_profile_photo(self._image(name="avatar.jpg"))
        with self.assertRaises(ValidationError):
            validate_profile_photo(SimpleUploadedFile(
                "large.png",
                b"x" * (MAX_PROFILE_PHOTO_SIZE + 1),
            ))

        self.client.force_login(self.hod)
        oversized_upload = self.client.post(
            reverse("my_profile"),
            {
                "profile_photo": SimpleUploadedFile(
                    "large.png",
                    b"x" * (MAX_PROFILE_PHOTO_SIZE + 1),
                    content_type="image/png",
                ),
            },
        )
        self.assertEqual(oversized_upload.status_code, 200)
        self.assertContains(oversized_upload, "5 MB or smaller")
        self.hod.refresh_from_db()
        self.assertFalse(self.hod.profile_photo)


class StudentSearchTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            username="student-search-admin",
            password="test-password",
            user_type="1",
        )
        self.client.force_login(self.admin)
        self.computer_science = Courses.objects.create(course_name="Computer Science")
        self.mathematics = Courses.objects.create(course_name="Mathematics")
        self.first_session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        self.second_session = SessionYearModel.objects.create(
            session_start_year=parse_date("2056-08-14"),
            session_end_year=parse_date("2057-05-30"),
        )
        self.maya_singh = self._create_student(
            "maya-singh",
            "Maya",
            "Singh",
            self.computer_science,
            self.first_session,
            "Female",
        )
        self._create_student(
            "arjun-rao",
            "Arjun",
            "Rao",
            self.computer_science,
            self.first_session,
            "Male",
        )
        self.maya_patel = self._create_student(
            "maya-patel",
            "Maya",
            "Patel",
            self.mathematics,
            self.second_session,
            "Female",
        )

    @staticmethod
    def _create_student(username, first_name, last_name, course, session, gender):
        user = CustomUser.objects.create_user(
            username=username,
            email=f"{username}@example.test",
            password="test-password",
            first_name=first_name,
            last_name=last_name,
            user_type="3",
        )
        return Students.objects.create(
            admin=user,
            gender=gender,
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )

    def test_keyword_and_filters_can_be_combined(self):
        response = self.client.get(reverse("manage_student"), {
            "q": "Maya",
            "course_id": self.mathematics.pk,
            "session_year_id": self.second_session.pk,
            "gender": "Female",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.maya_patel.admin.username)
        self.assertNotContains(response, self.maya_singh.admin.username)
        self.assertContains(response, "1 student found")

    def test_multi_word_search_matches_name_and_invalid_filters_do_not_show_all(self):
        response = self.client.get(reverse("manage_student"), {"q": "Maya Singh"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.maya_singh.admin.username)
        self.assertNotContains(response, self.maya_patel.admin.username)

        invalid_response = self.client.get(reverse("manage_student"), {"course_id": "999999"})
        self.assertEqual(invalid_response.status_code, 200)
        self.assertContains(invalid_response, "Please correct the invalid search filters.")
        self.assertContains(invalid_response, "0 students found")
        self.assertNotContains(invalid_response, self.maya_singh.admin.username)

    def test_student_list_remains_restricted_to_admin_role(self):
        self.client.logout()
        anonymous_response = self.client.get(reverse("manage_student"))
        self.assertRedirects(
            anonymous_response,
            reverse("login"),
            fetch_redirect_response=False,
        )

        staff_user = CustomUser.objects.create_user(
            username="student-search-staff",
            password="test-password",
            user_type="2",
        )
        self.client.force_login(staff_user)
        staff_response = self.client.get(reverse("manage_student"))
        self.assertRedirects(
            staff_response,
            reverse("staff_home"),
            fetch_redirect_response=False,
        )


class AttendanceEndpointSecurityTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            username="attendance-security-admin",
            password="test-password",
            user_type="1",
        )

    def test_attendance_endpoints_require_post_and_validate_ids(self):
        self.client.force_login(self.admin)
        dates_url = reverse("admin_get_attendance_dates")
        students_url = reverse("admin_get_attendance_student")

        self.assertEqual(self.client.get(dates_url).status_code, 405)
        self.assertEqual(self.client.get(students_url).status_code, 405)

        dates_response = self.client.post(dates_url, {
            "subject": "not-an-id",
            "session_year_id": "1",
        })
        students_response = self.client.post(students_url, {
            "attendance_date": "not-an-id",
        })
        self.assertEqual(dates_response.status_code, 400)
        self.assertEqual(students_response.status_code, 400)
        self.assertIn("error", dates_response.json())
        self.assertIn("error", students_response.json())

    def test_attendance_student_endpoint_returns_json_records(self):
        self.client.force_login(self.admin)
        course = Courses.objects.create(course_name="Attendance report course")
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        subject = Subjects.objects.create(
            subject_name="Attendance report subject",
            course_id=course,
            staff_id=self.admin,
        )
        student_user = CustomUser.objects.create_user(
            username="attendance-report-student",
            password="test-password",
            first_name="Jordan",
            last_name="Lee",
            user_type="3",
        )
        student = Students.objects.create(
            admin=student_user,
            gender="",
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )
        attendance = Attendance.objects.create(
            subject_id=subject,
            session_year_id=session,
            attendance_date=parse_date("2055-09-01"),
        )
        AttendanceReport.objects.create(
            student_id=student,
            attendance_id=attendance,
            status=True,
        )

        response = self.client.post(
            reverse("admin_get_attendance_student"),
            {"attendance_date": attendance.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            "id": student_user.pk,
            "name": "Jordan Lee",
            "status": True,
        }])

    def test_attendance_endpoints_enforce_csrf_tokens(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        page_response = csrf_client.get(reverse("admin_view_attendance"))
        self.assertEqual(page_response.status_code, 200)

        post_data = {"subject": "not-an-id", "session_year_id": "1"}
        endpoint = reverse("admin_get_attendance_dates")
        rejected_response = csrf_client.post(endpoint, post_data)
        self.assertEqual(rejected_response.status_code, 403)

        csrf_token = csrf_client.cookies["csrftoken"].value
        accepted_response = csrf_client.post(
            endpoint,
            post_data,
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(accepted_response.status_code, 400)
        self.assertIn("error", accepted_response.json())

    def test_hod_ajax_endpoints_require_post_and_csrf(self):
        self.client.force_login(self.admin)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        page_response = csrf_client.get(reverse("add_student"))
        self.assertEqual(page_response.status_code, 200)

        endpoint = reverse("check_email_exist")
        self.assertEqual(csrf_client.get(endpoint).status_code, 405)
        self.assertEqual(csrf_client.post(endpoint, {"email": "new@example.test"}).status_code, 403)

        csrf_token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(
            endpoint,
            {"email": "new@example.test", "csrfmiddlewaretoken": csrf_token},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"False")

    def test_staff_attendance_is_limited_to_assigned_subjects_and_csrf_protected(self):
        staff = CustomUser.objects.create_user(
            username="attendance-owner",
            password="test-password",
            user_type="2",
        )
        other_staff = CustomUser.objects.create_user(
            username="attendance-other-owner",
            password="test-password",
            user_type="2",
        )
        course = Courses.objects.create(course_name="Staff attendance course")
        session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        subject = Subjects.objects.create(
            subject_name="Owned subject",
            course_id=course,
            staff_id=staff,
        )
        other_subject = Subjects.objects.create(
            subject_name="Unowned subject",
            course_id=course,
            staff_id=other_staff,
        )
        student_user = CustomUser.objects.create_user(
            username="staff-attendance-student",
            password="test-password",
            first_name="Jordan",
            last_name="Lee",
            user_type="3",
        )
        student = Students.objects.create(
            admin=student_user,
            gender="",
            profile_pic="",
            address="",
            course_id=course,
            session_year_id=session,
        )
        attendance = Attendance.objects.create(
            subject_id=subject,
            session_year_id=session,
            attendance_date=parse_date("2055-09-01"),
        )
        other_attendance = Attendance.objects.create(
            subject_id=other_subject,
            session_year_id=session,
            attendance_date=parse_date("2055-09-02"),
        )
        report = AttendanceReport.objects.create(
            student_id=student,
            attendance_id=attendance,
            status=False,
        )
        AttendanceReport.objects.create(
            student_id=student,
            attendance_id=other_attendance,
            status=False,
        )
        self.client.force_login(staff)

        students_response = self.client.post(reverse("get_students"), {
            "subject": subject.pk,
            "session_year": session.pk,
        })
        self.assertEqual(students_response.status_code, 200)
        self.assertEqual(students_response.json(), [{
            "id": student_user.pk,
            "name": "Jordan Lee",
        }])
        self.assertEqual(
            self.client.post(reverse("get_students"), {
                "subject": other_subject.pk,
                "session_year": session.pk,
            }).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse("get_attendance_student"), {
                "attendance_date": attendance.pk,
            }).json()[0]["id"],
            student_user.pk,
        )
        self.assertEqual(
            self.client.post(reverse("get_attendance_student"), {
                "attendance_date": other_attendance.pk,
            }).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse("update_attendance_data"), {
                "attendance_date": other_attendance.pk,
                "student_ids": json.dumps([{"id": student_user.pk, "status": 1}]),
            }).status_code,
            404,
        )

        update_response = self.client.post(reverse("update_attendance_data"), {
            "attendance_date": attendance.pk,
            "student_ids": json.dumps([{"id": student_user.pk, "status": 1}]),
        })
        self.assertEqual(update_response.status_code, 200)
        report.refresh_from_db()
        self.assertTrue(report.status)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(staff)
        self.assertEqual(csrf_client.get(reverse("staff_take_attendance")).status_code, 200)
        self.assertEqual(
            csrf_client.post(reverse("get_students"), {
                "subject": subject.pk,
                "session_year": session.pk,
            }).status_code,
            403,
        )


class StaffResultSecurityTests(TestCase):
    def setUp(self):
        self.staff = CustomUser.objects.create_user(
            username="result-owner",
            password="test-password",
            user_type="2",
        )
        self.other_staff = CustomUser.objects.create_user(
            username="result-other-owner",
            password="test-password",
            user_type="2",
        )
        self.course = Courses.objects.create(course_name="Staff result course")
        self.session = SessionYearModel.objects.create(
            session_start_year=parse_date("2055-08-14"),
            session_end_year=parse_date("2056-05-30"),
        )
        self.subject = Subjects.objects.create(
            subject_name="Owned result subject",
            course_id=self.course,
            staff_id=self.staff,
        )
        self.other_subject = Subjects.objects.create(
            subject_name="Unowned result subject",
            course_id=self.course,
            staff_id=self.other_staff,
        )
        student_user = CustomUser.objects.create_user(
            username="result-owner-student",
            password="test-password",
            user_type="3",
        )
        self.student = Students.objects.create(
            admin=student_user,
            gender="",
            profile_pic="",
            address="",
            course_id=self.course,
            session_year_id=self.session,
        )
        self.client.force_login(self.staff)
        self.url = reverse("staff_add_result_save")

    def _post_result(self, **overrides):
        data = {
            "student_list": self.student.admin_id,
            "subject": self.subject.pk,
            "session_year": self.session.pk,
            "assignment_marks": "78.5",
            "exam_marks": "86",
        }
        data.update(overrides)
        return self.client.post(self.url, data)

    def test_staff_can_create_and_update_results_for_their_enrolled_students(self):
        response = self._post_result()
        self.assertRedirects(response, reverse("staff_add_result"), fetch_redirect_response=False)
        result = StudentResult.objects.get(student_id=self.student, subject_id=self.subject)
        self.assertEqual(result.subject_assignment_marks, 78.5)
        self.assertEqual(result.subject_exam_marks, 86)

        self._post_result(assignment_marks="80")
        result.refresh_from_db()
        self.assertEqual(result.subject_assignment_marks, 80)

    def test_staff_cannot_change_unassigned_or_mismatched_results(self):
        unassigned_response = self._post_result(subject=self.other_subject.pk)
        self.assertEqual(unassigned_response.status_code, 404)

        other_course = Courses.objects.create(course_name="Different result course")
        other_student_user = CustomUser.objects.create_user(
            username="outside-result-student",
            password="test-password",
            user_type="3",
        )
        other_student = Students.objects.create(
            admin=other_student_user,
            gender="",
            profile_pic="",
            address="",
            course_id=other_course,
            session_year_id=self.session,
        )
        mismatch_response = self._post_result(student_list=other_student.admin_id)
        self.assertEqual(mismatch_response.status_code, 404)
        self.assertFalse(StudentResult.objects.exists())

    def test_result_marks_must_be_valid_and_non_negative(self):
        for invalid_value in ("not-a-number", "-1", "NaN", "Infinity", "1e10000"):
            with self.subTest(value=invalid_value):
                response = self._post_result(exam_marks=invalid_value)
                self.assertRedirects(
                    response,
                    reverse("staff_add_result"),
                    fetch_redirect_response=False,
                )
        self.assertFalse(StudentResult.objects.exists())


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
