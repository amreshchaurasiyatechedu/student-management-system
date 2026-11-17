import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.static import serve
from django.views.decorators.cache import never_cache

from .forms import ProfileDirectoryFilterForm, ProfilePhotoForm
from .models import Courses, CustomUser, SessionYearModel, Staffs, Students, Subjects
from .validators import validate_profile_photo


ROLE_LABELS = {
    "1": "HOD",
    "2": "Staff / Teacher",
    "3": "Student",
}
logger = logging.getLogger(__name__)


def _base_template(user):
    return {
        "1": "hod_template/base_template.html",
        "2": "staff_template/base_template.html",
        "3": "student_template/base_template.html",
    }.get(user.user_type)


def _assigned_subjects(user):
    return Subjects.objects.filter(staff_id=user).select_related(
        "course_id",
    ).order_by("course_id__course_name", "subject_name")


def _assigned_students(user):
    course_ids = _assigned_subjects(user).values_list("course_id", flat=True)
    return Students.objects.filter(course_id__in=course_ids)


def _delete_previous_photo(storage, name):
    try:
        storage.delete(name)
    except PermissionError:
        logger.warning("A replaced profile photo is still in use and could not be deleted.")
        return False
    return True


def _save_profile_photo(
    request,
    profile_user,
    form,
    previous_photo_name,
    photo_storage,
):
    new_photo = form.files.get("profile_photo")

    if form.cleaned_data.get("clear_photo"):
        profile_user.profile_photo = ""
    elif new_photo:
        profile_user.profile_photo = new_photo
    else:
        messages.info(request, "Choose a photo to upload or select remove.")
        return False

    profile_user.save(update_fields=["profile_photo"])
    previous_photo_deleted = True
    if previous_photo_name and previous_photo_name != profile_user.profile_photo.name:
        previous_photo_deleted = _delete_previous_photo(
            photo_storage,
            previous_photo_name,
        )
    if previous_photo_deleted:
        messages.success(request, "Profile photo updated.")
    else:
        messages.warning(
            request,
            "Your profile photo was updated, but the previous file is still in use and could not be removed.",
        )
    return True


def _can_view_profile(actor, target):
    if actor.pk == target.pk:
        return True
    if actor.user_type == "1":
        return target.user_type in {"2", "3"}
    if actor.user_type == "2" and target.user_type == "3":
        return _assigned_students(actor).filter(admin_id=target.pk).exists()
    return False


def _profile_rows(users, actor, subjects_by_course=None):
    rows = []
    for profile_user in users:
        if profile_user.user_type == "3":
            student = getattr(profile_user, "students", None)
            if student is None:
                continue
            subjects = (
                subjects_by_course.get(student.course_id_id, [])
                if subjects_by_course is not None
                else Subjects.objects.filter(course_id=student.course_id)
                .order_by("subject_name")
                .values_list("subject_name", flat=True)
            )
            rows.append({
                "profile_user": profile_user,
                "role_label": ROLE_LABELS["3"],
                "record_id": student.pk,
                "course_name": student.course_id.course_name,
                "session_name": student.session_year_id.display_name,
                "subjects": subjects,
            })
        elif profile_user.user_type == "2":
            staff = getattr(profile_user, "staffs", None)
            if staff is None:
                continue
            taught_subjects = list(
                Subjects.objects.filter(staff_id=profile_user)
                .select_related("course_id")
                .order_by("subject_name")
            )
            rows.append({
                "profile_user": profile_user,
                "role_label": ROLE_LABELS["2"],
                "record_id": staff.pk,
                "course_name": ", ".join(sorted({
                    subject.course_id.course_name for subject in taught_subjects
                })),
                "session_name": "",
                "subjects": [subject.subject_name for subject in taught_subjects],
            })
    return rows


def _page_context(request, items, row_builder):
    paginator = Paginator(items, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    query = request.GET.copy()

    def page_url(page_number):
        query["page"] = page_number
        return f"?{query.urlencode()}"

    return {
        "rows": row_builder(page_obj.object_list),
        "page_obj": page_obj,
        "previous_page_url": (
            page_url(page_obj.previous_page_number()) if page_obj.has_previous() else None
        ),
        "next_page_url": (
            page_url(page_obj.next_page_number()) if page_obj.has_next() else None
        ),
    }


def _profile_details(profile_user, viewer=None):
    student = getattr(profile_user, "students", None)
    staff = getattr(profile_user, "staffs", None)
    subjects = _assigned_subjects(profile_user) if profile_user.user_type == "2" else []
    if student:
        subjects = Subjects.objects.filter(
            course_id=student.course_id,
        ).order_by("subject_name")
        if viewer is not None and viewer.user_type == "2":
            subjects = subjects.filter(staff_id=viewer)
    return student, staff, subjects


@login_required
@never_cache
def my_profile(request):
    profile_user = request.user
    base_template = _base_template(profile_user)
    if base_template is None:
        raise Http404

    current_photo = profile_user.profile_photo
    current_photo_name = current_photo.name if current_photo else ""
    photo_storage = current_photo.storage
    form = ProfilePhotoForm(instance=profile_user)
    if request.method == "POST":
        form = ProfilePhotoForm(
            request.POST,
            request.FILES,
            instance=profile_user,
        )
        if form.is_valid() and _save_profile_photo(
            request,
            profile_user,
            form,
            current_photo_name,
            photo_storage,
        ):
            return redirect("my_profile")

    student, staff, subjects = _profile_details(profile_user)
    return render(request, "profiles/my_profile.html", {
        "base_template": base_template,
        "profile_user": profile_user,
        "role_label": ROLE_LABELS[profile_user.user_type],
        "photo_form": form,
        "student": student,
        "staff": staff,
        "subjects": subjects,
    })


@login_required
@never_cache
def user_directory(request):
    if request.user.user_type != "1":
        raise Http404

    form = ProfileDirectoryFilterForm(request.GET)
    users = CustomUser.objects.filter(
        user_type__in=("2", "3"),
    ).select_related(
        "students__course_id",
        "students__session_year_id",
        "staffs",
    ).order_by("last_name", "first_name", "pk")

    if form.is_valid():
        query = form.cleaned_data["q"].strip()
        for term in query.split():
            criteria = (
                Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
                | Q(username__icontains=term)
                | Q(email__icontains=term)
            )
            role = {
                "student": "3",
                "students": "3",
                "staff": "2",
                "teacher": "2",
                "teachers": "2",
            }.get(term.casefold())
            if role:
                criteria |= Q(user_type=role)
            if term.isdecimal():
                criteria |= Q(students__id=int(term)) | Q(staffs__id=int(term))
            users = users.filter(criteria)

        role = form.cleaned_data["role"]
        if role:
            users = users.filter(user_type=role)

        course = form.cleaned_data["course_id"]
        if course:
            users = users.filter(
                Q(user_type="3", students__course_id=course)
                | Q(user_type="2", subjects__course_id=course)
            )

        subject = form.cleaned_data["subject_id"]
        if subject:
            users = users.filter(
                Q(user_type="2", subjects=subject)
                | Q(user_type="3", students__course_id=subject.course_id)
            )

        session = form.cleaned_data["session_year_id"]
        if session:
            users = users.filter(
                user_type="3",
                students__session_year_id=session,
            )
    else:
        users = users.none()

    users = users.distinct()
    page_context = _page_context(
        request,
        users,
        lambda page_users: _profile_rows(page_users, request.user),
    )
    return render(request, "profiles/user_directory.html", {
        "base_template": _base_template(request.user),
        "filter_form": form,
        "show_role_filter": True,
        **page_context,
    })


@login_required
@never_cache
def staff_student_directory(request):
    if request.user.user_type != "2":
        raise Http404

    assigned_subjects = _assigned_subjects(request.user)
    course_ids = assigned_subjects.values_list("course_id", flat=True)
    courses = Courses.objects.filter(pk__in=course_ids).order_by("course_name")
    form = ProfileDirectoryFilterForm(
        request.GET,
        courses=courses,
        subjects=assigned_subjects,
    )
    students = Students.objects.filter(
        course_id__in=course_ids,
    ).select_related(
        "admin",
        "course_id",
        "session_year_id",
    ).order_by("admin__last_name", "admin__first_name", "pk")

    if form.is_valid():
        query = form.cleaned_data["q"].strip()
        for term in query.split():
            criteria = (
                Q(admin__first_name__icontains=term)
                | Q(admin__last_name__icontains=term)
                | Q(admin__username__icontains=term)
            )
            if term.isdecimal():
                criteria |= Q(pk=int(term))
            students = students.filter(criteria)

        course = form.cleaned_data["course_id"]
        if course:
            students = students.filter(course_id=course)
        subject = form.cleaned_data["subject_id"]
        if subject:
            students = students.filter(course_id=subject.course_id)
        session = form.cleaned_data["session_year_id"]
        if session:
            students = students.filter(session_year_id=session)
    else:
        students = students.none()

    subjects_by_course = {}
    for subject in assigned_subjects:
        subjects_by_course.setdefault(subject.course_id_id, []).append(
            subject.subject_name,
        )
    def student_rows(page_students):
        return [
            {
                "profile_user": student.admin,
                "role_label": ROLE_LABELS["3"],
                "record_id": student.pk,
                "course_name": student.course_id.course_name,
                "session_name": student.session_year_id.display_name,
                "subjects": subjects_by_course.get(student.course_id_id, []),
            }
            for student in page_students
        ]

    page_context = _page_context(request, students, student_rows)
    return render(request, "profiles/user_directory.html", {
        "base_template": _base_template(request.user),
        "filter_form": form,
        "show_role_filter": False,
        **page_context,
    })


@login_required
@never_cache
def profile_detail(request, user_id):
    profile_user = get_object_or_404(CustomUser, pk=user_id)
    if not _can_view_profile(request.user, profile_user):
        raise Http404

    can_manage_profile_photo = (
        request.user.user_type == "1"
        and profile_user.user_type in {"2", "3"}
    )
    photo_form = None
    if can_manage_profile_photo:
        current_photo = profile_user.profile_photo
        current_photo_name = current_photo.name if current_photo else ""
        photo_storage = current_photo.storage
        photo_form = ProfilePhotoForm(instance=profile_user)
        if request.method == "POST":
            photo_form = ProfilePhotoForm(
                request.POST,
                request.FILES,
                instance=profile_user,
            )
            if photo_form.is_valid() and _save_profile_photo(
                request,
                profile_user,
                photo_form,
                current_photo_name,
                photo_storage,
            ):
                return redirect("profile_detail", user_id=profile_user.pk)
    elif request.method == "POST":
        raise Http404

    base_template = _base_template(request.user)
    if base_template is None:
        raise Http404
    student, staff, subjects = _profile_details(profile_user, request.user)
    return render(request, "profiles/profile_detail.html", {
        "base_template": base_template,
        "profile_user": profile_user,
        "role_label": ROLE_LABELS.get(profile_user.user_type, "User"),
        "is_own_profile": request.user.pk == profile_user.pk,
        "is_staff_viewing_student": (
            request.user.user_type == "2" and profile_user.user_type == "3"
        ),
        "show_admin_details": request.user.user_type == "1",
        "can_manage_profile_photo": can_manage_profile_photo,
        "photo_form": photo_form,
        "student": student,
        "staff": staff,
        "subjects": subjects,
    })


@login_required
@never_cache
def profile_photo(request, user_id):
    profile_user = get_object_or_404(CustomUser, pk=user_id)
    if not _can_view_profile(request.user, profile_user):
        raise Http404
    if not profile_user.profile_photo:
        raise Http404

    storage = profile_user.profile_photo.storage
    photo_name = profile_user.profile_photo.name
    if not storage.exists(photo_name):
        raise Http404
    try:
        photo_file = storage.open(photo_name, "rb")
    except FileNotFoundError as error:
        raise Http404 from error

    content_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(Path(photo_name).suffix.lower())
    if content_type is None:
        photo_file.close()
        raise Http404

    response = FileResponse(photo_file, content_type=content_type)
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


def secure_media_file(request, stored_path):
    if stored_path.startswith("profile_photos/") or not settings.DEBUG:
        raise Http404

    media_prefix = settings.MEDIA_URL.strip("/")
    legacy_names = {
        stored_path,
        f"/{stored_path}",
        f"{settings.MEDIA_URL}{stored_path}",
        f"/{media_prefix}/{stored_path}",
        f"{media_prefix}/{stored_path}",
    }
    legacy_student = Students.objects.select_related("admin").filter(
        Q(profile_pic__in=legacy_names)
        | Q(profile_pic__endswith=f"/{stored_path}"),
    ).first()
    if legacy_student is None:
        return serve(request, stored_path, document_root=settings.MEDIA_ROOT)
    if not _can_view_profile(request.user, legacy_student.admin):
        raise Http404

    try:
        photo_file = default_storage.open(stored_path, "rb")
    except FileNotFoundError as error:
        raise Http404 from error
    try:
        validate_profile_photo(photo_file)
    except ValidationError as error:
        photo_file.close()
        raise Http404 from error

    content_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(Path(stored_path).suffix.lower())
    if content_type is None:
        photo_file.close()
        raise Http404

    response = FileResponse(photo_file, content_type=content_type)
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
