import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from django.shortcuts import get_object_or_404
from django.core import serializers
import json

from student_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport
from .forms import AddStudentForm, EditStudentForm, SessionYearForm, StudentSearchForm
from .utils import _positive_id


logger = logging.getLogger(__name__)


def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')




def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


def manage_session(request):
    session_years = SessionYearModel.objects.order_by("session_start_year", "session_end_year")
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("add_session")

    form = SessionYearForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Session Year added Successfully!")
    else:
        messages.error(request, "; ".join(
            error for errors in form.errors.values() for error in errors
        ))
    return redirect("add_session")


def edit_session(request, session_id):
    session_year = get_object_or_404(SessionYearModel, id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    session_id = request.POST.get("session_id")
    session_year = get_object_or_404(SessionYearModel, id=session_id)
    form = SessionYearForm(request.POST, instance=session_year)
    if form.is_valid():
        form.save()
        messages.success(request, "Session Year Updated Successfully.")
    else:
        messages.error(request, "; ".join(
            error for errors in form.errors.values() for error in errors
        ))
    return redirect("edit_session", session_id=session_year.id)


def delete_session(request, session_id):
    session = get_object_or_404(SessionYearModel, id=session_id)
    if Students.objects.filter(session_year_id=session).exists() or Attendance.objects.filter(session_year_id=session).exists():
        messages.error(request, "This session is in use by students or attendance records and cannot be deleted.")
    else:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
    return redirect("manage_session")


def _session_payload(request):
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        return payload if isinstance(payload, dict) else None
    return request.POST


def _session_data(session_year):
    return {
        "id": session_year.id,
        "session_name": session_year.session_name,
        "display_name": session_year.display_name,
        "session_start_year": session_year.session_start_year.isoformat(),
        "session_end_year": session_year.session_end_year.isoformat(),
    }


@require_http_methods(["GET", "POST"])
def session_years_api(request):
    if request.method == "GET":
        sessions = SessionYearModel.objects.order_by("session_start_year", "session_end_year")
        return JsonResponse({"sessions": [_session_data(session) for session in sessions]})

    payload = _session_payload(request)
    if payload is None:
        return JsonResponse({"error": "Request body must contain valid session data."}, status=400)

    form = SessionYearForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    session_year = form.save()
    return JsonResponse({"session": _session_data(session_year)}, status=201)


@require_http_methods(["PUT", "PATCH", "DELETE"])
def session_year_api(request, session_id):
    session_year = get_object_or_404(SessionYearModel, id=session_id)

    if request.method == "DELETE":
        if Students.objects.filter(session_year_id=session_year).exists() or Attendance.objects.filter(session_year_id=session_year).exists():
            return JsonResponse(
                {"error": "This session is in use by students or attendance records and cannot be deleted."},
                status=409,
            )
        session_year.delete()
        return JsonResponse({"deleted": True})

    payload = _session_payload(request)
    if payload is None:
        return JsonResponse({"error": "Request body must contain valid session data."}, status=400)
    form_data = {
        "session_name": payload.get("session_name", session_year.session_name),
        "session_start_year": payload.get("session_start_year", session_year.session_start_year.isoformat()),
        "session_end_year": payload.get("session_end_year", session_year.session_end_year.isoformat()),
    }
    form = SessionYearForm(form_data, instance=session_year)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    session_year = form.save()
    return JsonResponse({"session": _session_data(session_year)})


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            profile_photo = form.cleaned_data.get("profile_pic")

            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=3,
                    profile_photo=profile_photo or "",
                )
                user.students.address = address

                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_year_obj

                user.students.gender = gender
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except:
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
        else:
            return redirect('add_student')


def manage_student(request):
    search_form = StudentSearchForm(request.GET)
    students = Students.objects.select_related(
        "admin",
        "course_id",
        "session_year_id",
    ).order_by("admin__last_name", "admin__first_name", "pk")

    if search_form.is_valid():
        cleaned_data = search_form.cleaned_data
        for term in cleaned_data["q"].split():
            students = students.filter(
                Q(admin__first_name__icontains=term)
                | Q(admin__last_name__icontains=term)
                | Q(admin__username__icontains=term)
                | Q(admin__email__icontains=term)
                | Q(address__icontains=term)
                | Q(course_id__course_name__icontains=term)
                | Q(session_year_id__session_name__icontains=term)
            )
        if cleaned_data["course_id"]:
            students = students.filter(course_id=cleaned_data["course_id"])
        if cleaned_data["session_year_id"]:
            students = students.filter(session_year_id=cleaned_data["session_year_id"])
        if cleaned_data["gender"]:
            students = students.filter(gender=cleaned_data["gender"])
    else:
        students = students.none()

    paginator = Paginator(students, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    def page_url(page_number):
        query_params = request.GET.copy()
        query_params["page"] = page_number
        return f"?{query_params.urlencode()}"

    context = {
        "students": page_obj.object_list,
        "search_form": search_form,
        "page_obj": page_obj,
        "paginator": paginator,
        "previous_page_url": (
            page_url(page_obj.previous_page_number()) if page_obj.has_previous() else None
        ),
        "next_page_url": page_url(page_obj.next_page_number()) if page_obj.has_next() else None,
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['course_id'].initial = student.course_id.id
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id.id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']
            profile_photo = form.cleaned_data.get("profile_pic")

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                old_profile_photo = user.profile_photo
                old_profile_photo_name = (
                    old_profile_photo.name if old_profile_photo else ""
                )
                profile_photo_storage = old_profile_photo.storage
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                if profile_photo:
                    user.profile_photo = profile_photo
                user.save()
                old_photo_deleted = True
                if (
                    profile_photo
                    and old_profile_photo_name
                    and old_profile_photo_name != user.profile_photo.name
                ):
                    try:
                        profile_photo_storage.delete(old_profile_photo_name)
                    except PermissionError:
                        logger.warning(
                            "A replaced student profile photo is still in use and could not be deleted."
                        )
                        old_photo_deleted = False

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                course = Courses.objects.get(id=course_id)
                student_model.course_id = course

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                if old_photo_deleted:
                    messages.success(request, "Student Updated Successfully!")
                else:
                    messages.warning(
                        request,
                        "Student updated, but the previous profile photo file is still in use and could not be removed.",
                    )
                return redirect('/edit_student/'+student_id)
            except:
                messages.success(request, "Failed to Uupdate Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@require_POST
def check_email_exist(request):
    email = request.POST.get("email", "").strip()
    if not email:
        return HttpResponseBadRequest("Email is required.")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@require_POST
def check_username_exist(request):
    username = request.POST.get("username", "").strip()
    if not username:
        return HttpResponseBadRequest("Username is required.")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@require_POST
def student_feedback_message_reply(request):
    feedback_id = _positive_id(request.POST.get("id"))
    feedback_reply = request.POST.get("reply", "").strip()
    if feedback_id is None or not feedback_reply:
        return HttpResponseBadRequest("A valid feedback ID and reply are required.")

    feedback = get_object_or_404(FeedBackStudent, id=feedback_id)
    feedback.feedback_reply = feedback_reply
    feedback.save(update_fields=["feedback_reply", "updated_at"])
    return HttpResponse("True")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@require_POST
def staff_feedback_message_reply(request):
    feedback_id = _positive_id(request.POST.get("id"))
    feedback_reply = request.POST.get("reply", "").strip()
    if feedback_id is None or not feedback_reply:
        return HttpResponseBadRequest("A valid feedback ID and reply are required.")

    feedback = get_object_or_404(FeedBackStaffs, id=feedback_id)
    feedback.feedback_reply = feedback_reply
    feedback.save(update_fields=["feedback_reply", "updated_at"])
    return HttpResponse("True")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@require_POST
def admin_get_attendance_dates(request):
    subject_id = _positive_id(request.POST.get("subject"))
    session_year_id = _positive_id(request.POST.get("session_year_id"))
    if subject_id is None or session_year_id is None:
        return JsonResponse(
            {"error": "Select a valid subject and academic session."},
            status=400,
        )

    subject_model = get_object_or_404(Subjects, id=subject_id)
    session_model = get_object_or_404(SessionYearModel, id=session_year_id)

    attendance = Attendance.objects.filter(
        subject_id=subject_model,
        session_year_id=session_model,
        attendance_date__range=(session_model.session_start_year, session_model.session_end_year),
    ).order_by("attendance_date")

    list_data = [
        {
            "id": attendance_record.id,
            "attendance_date": str(attendance_record.attendance_date),
            "session_year_id": attendance_record.session_year_id_id,
        }
        for attendance_record in attendance
    ]
    return JsonResponse(list_data, safe=False)


@require_POST
def admin_get_attendance_student(request):
    attendance_id = _positive_id(request.POST.get("attendance_date"))
    if attendance_id is None:
        return JsonResponse({"error": "Select a valid attendance date."}, status=400)
    attendance = get_object_or_404(Attendance, id=attendance_id)

    attendance_data = AttendanceReport.objects.filter(
        attendance_id=attendance,
    ).select_related("student_id__admin")
    list_data = [
        {
            "id": report.student_id.admin_id,
            "name": f"{report.student_id.admin.first_name} {report.student_id.admin.last_name}".strip(),
            "status": report.status,
        }
        for report in attendance_data
    ]
    return JsonResponse(list_data, safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def staff_profile(request):
    pass


def student_profile(requtest):
    pass
