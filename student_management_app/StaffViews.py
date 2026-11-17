from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db import transaction
import datetime
from django.core import serializers
from decimal import Decimal, InvalidOperation
import json
import math


from student_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, Attendance, AttendanceReport, LeaveReportStaff, FeedBackStaffs, StudentResult
from .utils import _positive_id


def staff_home(request):
    # Fetching All Students under Staff

    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_id_list = []
    for subject in subjects:
        course = Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)
    
    final_course = []
    # Removing Duplicate Course Id
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)
    
    students_count = Students.objects.filter(course_id__in=final_course).count()
    subject_count = subjects.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    # Fetch All Approve Leave
    staff = Staffs.objects.get(admin=request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()

    #Fetch Attendance Data by Subjects
    subject_list = []
    attendance_list = []
    for subject in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance = Students.objects.filter(course_id__in=final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    for student in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, student_id=student.id).count()
        student_list.append(student.admin.first_name+" "+ student.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context={
        "students_count": students_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent
    }
    return render(request, "staff_template/staff_home_template.html", context)



def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/take_attendance_template.html", context)


def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')
        try:
            leave_date = datetime.date.fromisoformat(leave_date).isoformat()
        except (TypeError, ValueError):
            messages.error(request, "Enter a valid leave date.")
            return redirect("staff_apply_leave")

        staff_obj = Staffs.objects.get(admin=request.user.id)
        leave_report = LeaveReportStaff(staff_id=staff_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
        leave_report.save()
        messages.success(request, "Applied for Leave.")
        return redirect('staff_apply_leave')


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "staff_template/staff_feedback_template.html", context)


def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('staff_feedback')


@require_POST
def get_students(request):
    subject_id = _positive_id(request.POST.get("subject"))
    session_year_id = _positive_id(request.POST.get("session_year"))
    if subject_id is None or session_year_id is None:
        return HttpResponseBadRequest("Select a valid subject and session.")

    subject = get_object_or_404(Subjects, id=subject_id, staff_id=request.user.id)
    session_year = get_object_or_404(SessionYearModel, id=session_year_id)
    students = Students.objects.filter(
        course_id=subject.course_id,
        session_year_id=session_year,
    ).select_related("admin")
    list_data = [
        {
            "id": student.admin_id,
            "name": f"{student.admin.first_name} {student.admin.last_name}".strip(),
        }
        for student in students
    ]
    return JsonResponse(list_data, safe=False)


@require_POST
def save_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    subject_id = _positive_id(request.POST.get("subject_id"))
    attendance_date = request.POST.get("attendance_date")
    session_year_id = _positive_id(request.POST.get("session_year_id"))

    if not all((student_ids, subject_id, attendance_date, session_year_id)):
        return HttpResponse("Missing attendance data.", status=400)
    try:
        attendance_day = datetime.date.fromisoformat(attendance_date)
        json_student = json.loads(student_ids)
    except (TypeError, ValueError, json.JSONDecodeError):
        return HttpResponse("Invalid attendance date or student data.", status=400)

    subject_model = get_object_or_404(Subjects, id=subject_id, staff_id=request.user.id)
    session_year_model = get_object_or_404(SessionYearModel, id=session_year_id)
    if not session_year_model.session_start_year <= attendance_day <= session_year_model.session_end_year:
        return HttpResponse("Attendance date must be within the selected session.", status=400)
    if not isinstance(json_student, list):
        return HttpResponse("Invalid student data.", status=400)
    if not json_student:
        return HttpResponse("Select at least one student for attendance.", status=400)

    normalized_students = []
    for student_data in json_student:
        if not isinstance(student_data, dict):
            return HttpResponse("Invalid student data.", status=400)
        student_admin_id = _positive_id(student_data.get("id"))
        status = student_data.get("status")
        if student_admin_id is None or not isinstance(status, (int, bool)) or status not in (0, 1):
            return HttpResponse("Invalid student data.", status=400)
        normalized_students.append((student_admin_id, bool(status)))

    student_admin_ids = [student_id for student_id, _ in normalized_students]
    if len(student_admin_ids) != len(set(student_admin_ids)):
        return HttpResponse("Student list contains duplicates.", status=400)

    students = Students.objects.filter(
        admin_id__in=student_admin_ids,
        course_id=subject_model.course_id,
        session_year_id=session_year_model,
    )
    students_by_admin_id = {student.admin_id: student for student in students}
    if len(students_by_admin_id) != len(normalized_students):
        return HttpResponse("Student list does not match the selected subject and session.", status=400)

    with transaction.atomic():
        attendance = Attendance.objects.create(
            subject_id=subject_model,
            attendance_date=attendance_day,
            session_year_id=session_year_model,
        )
        AttendanceReport.objects.bulk_create([
            AttendanceReport(
                student_id=students_by_admin_id[student_admin_id],
                attendance_id=attendance,
                status=status,
            )
            for student_admin_id, status in normalized_students
        ])
    return HttpResponse("OK")


def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)


@require_POST
def get_attendance_dates(request):
    subject_id = _positive_id(request.POST.get("subject"))
    session_year_id = _positive_id(request.POST.get("session_year_id"))
    if subject_id is None or session_year_id is None:
        return HttpResponseBadRequest("Select a valid subject and session.")

    subject = get_object_or_404(Subjects, id=subject_id, staff_id=request.user.id)
    session_year = get_object_or_404(SessionYearModel, id=session_year_id)
    attendance = Attendance.objects.filter(
        subject_id=subject,
        session_year_id=session_year,
        attendance_date__range=(session_year.session_start_year, session_year.session_end_year),
    ).order_by("attendance_date")
    list_data = [
        {
            "id": record.id,
            "attendance_date": str(record.attendance_date),
            "session_year_id": record.session_year_id_id,
        }
        for record in attendance
    ]
    return JsonResponse(list_data, safe=False)


@require_POST
def get_attendance_student(request):
    attendance_id = _positive_id(request.POST.get("attendance_date"))
    if attendance_id is None:
        return HttpResponseBadRequest("Select a valid attendance record.")

    attendance = get_object_or_404(
        Attendance.objects.select_related("subject_id"),
        id=attendance_id,
        subject_id__staff_id=request.user.id,
    )
    attendance_reports = AttendanceReport.objects.filter(
        attendance_id=attendance,
    ).select_related("student_id__admin")
    list_data = [
        {
            "id": report.student_id.admin_id,
            "name": f"{report.student_id.admin.first_name} {report.student_id.admin.last_name}".strip(),
            "status": report.status,
        }
        for report in attendance_reports
    ]
    return JsonResponse(list_data, safe=False)


@require_POST
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    attendance_id = _positive_id(request.POST.get("attendance_date"))
    if not student_ids or attendance_id is None:
        return HttpResponseBadRequest("Attendance data is required.")
    try:
        submitted_students = json.loads(student_ids)
    except (TypeError, ValueError, json.JSONDecodeError):
        return HttpResponse("Invalid student data.", status=400)
    if not isinstance(submitted_students, list) or not submitted_students:
        return HttpResponseBadRequest("Select at least one student.")

    normalized_students = {}
    for student_data in submitted_students:
        if not isinstance(student_data, dict):
            return HttpResponseBadRequest("Invalid student data.")
        student_id = _positive_id(student_data.get("id"))
        status = student_data.get("status")
        if student_id is None or not isinstance(status, (int, bool)) or status not in (0, 1):
            return HttpResponseBadRequest("Invalid student data.")
        if student_id in normalized_students:
            return HttpResponseBadRequest("Student list contains duplicates.")
        normalized_students[student_id] = bool(status)

    attendance = get_object_or_404(
        Attendance,
        id=attendance_id,
        subject_id__staff_id=request.user.id,
    )
    reports = list(
        AttendanceReport.objects.filter(
            attendance_id=attendance,
            student_id__admin_id__in=normalized_students,
        ).select_related("student_id")
    )
    if len(reports) != len(normalized_students):
        return HttpResponseBadRequest("Student list does not match this attendance record.")

    with transaction.atomic():
        for report in reports:
            report.status = normalized_students[report.student_id.admin_id]
            report.save(update_fields=["status", "updated_at"])
    return HttpResponse("OK")


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context={
        "user": user,
        "staff": staff
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')



def staff_add_result(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years,
    }
    return render(request, "staff_template/add_result_template.html", context)


@require_POST
def staff_add_result_save(request):
    student_admin_id = _positive_id(request.POST.get("student_list"))
    subject_id = _positive_id(request.POST.get("subject"))
    session_year_id = _positive_id(request.POST.get("session_year"))
    try:
        assignment_marks = Decimal(request.POST.get("assignment_marks", "").strip())
        exam_marks = Decimal(request.POST.get("exam_marks", "").strip())
    except (InvalidOperation, AttributeError):
        messages.error(request, "Enter valid numeric marks.")
        return redirect("staff_add_result")

    if (
        student_admin_id is None
        or subject_id is None
        or session_year_id is None
        or not assignment_marks.is_finite()
        or not exam_marks.is_finite()
        or assignment_marks < 0
        or exam_marks < 0
    ):
        messages.error(request, "Enter valid non-negative marks and select a student, subject, and session.")
        return redirect("staff_add_result")
    assignment_value = float(assignment_marks)
    exam_value = float(exam_marks)
    if not math.isfinite(assignment_value) or not math.isfinite(exam_value):
        messages.error(request, "Marks are outside the supported numeric range.")
        return redirect("staff_add_result")

    subject = get_object_or_404(
        Subjects,
        id=subject_id,
        staff_id=request.user.id,
    )
    session_year = get_object_or_404(SessionYearModel, id=session_year_id)
    student = get_object_or_404(
        Students,
        admin_id=student_admin_id,
        course_id=subject.course_id,
        session_year_id=session_year,
    )
    result, created = StudentResult.objects.update_or_create(
        subject_id=subject,
        student_id=student,
        defaults={
            "subject_assignment_marks": assignment_value,
            "subject_exam_marks": exam_value,
        },
    )
    messages.success(
        request,
        "Result Added Successfully!" if created else "Result Updated Successfully!",
    )
    return redirect("staff_add_result")
