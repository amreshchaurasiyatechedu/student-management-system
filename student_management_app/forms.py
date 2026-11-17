from django import forms
from django.db.models import Q
from student_management_app.models import Attendance, Courses, SessionYearModel


class DateInput(forms.DateInput):
    input_type = "date"


class SessionYearForm(forms.ModelForm):
    class Meta:
        model = SessionYearModel
        fields = ("session_name", "session_start_year", "session_end_year")
        widgets = {
            "session_name": forms.TextInput(attrs={"class": "form-control"}),
            "session_start_year": DateInput(attrs={"class": "form-control"}),
            "session_end_year": DateInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("session_start_year")
        end_date = cleaned_data.get("session_end_year")

        if start_date and end_date:
            if end_date < start_date:
                self.add_error("session_end_year", "End date must be on or after the start date.")
            elif SessionYearModel.objects.filter(
                session_start_year=start_date,
                session_end_year=end_date,
            ).exclude(pk=self.instance.pk).exists():
                self.add_error(None, "A session with these dates already exists.")
            elif self.instance.pk and Attendance.objects.filter(
                session_year_id=self.instance,
            ).filter(
                Q(attendance_date__lt=start_date) | Q(attendance_date__gt=end_date)
            ).exists():
                self.add_error(
                    "session_end_year",
                    "The date range cannot exclude existing attendance records.",
                )

        return cleaned_data


class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    course_id = forms.ChoiceField(label="Course", choices=(), widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=(), widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_id"].choices = [
            (course.id, course.course_name) for course in Courses.objects.all()
        ]
        self.fields["session_year_id"].choices = [
            (session.id, session.display_name) for session in SessionYearModel.objects.all()
        ]


class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    course_id = forms.ChoiceField(label="Course", choices=(), widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=(), widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_id"].choices = [
            (course.id, course.course_name) for course in Courses.objects.all()
        ]
        self.fields["session_year_id"].choices = [
            (session.id, session.display_name) for session in SessionYearModel.objects.all()
        ]