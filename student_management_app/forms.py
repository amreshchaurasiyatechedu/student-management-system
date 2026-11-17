from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from student_management_app.models import (
    Attendance,
    Courses,
    CustomUser,
    SessionYearModel,
    Subjects,
)
from student_management_app.validators import (
    MAX_PROFILE_PHOTO_SIZE,
    validate_profile_photo,
)


class ProfileImageField(forms.ImageField):
    def to_python(self, data):
        if hasattr(data, "size") and data.size > MAX_PROFILE_PHOTO_SIZE:
            raise ValidationError("Profile photos must be 5 MB or smaller.")
        return super().to_python(data)


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
    profile_pic = ProfileImageField(
        label="Profile Pic",
        required=False,
        validators=[validate_profile_photo],
        widget=forms.FileInput(attrs={
            "class": "form-control-file",
            "accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp",
        }),
    )

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
    profile_pic = ProfileImageField(
        label="Profile Pic",
        required=False,
        validators=[validate_profile_photo],
        widget=forms.FileInput(attrs={
            "class": "form-control-file",
            "accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_id"].choices = [
            (course.id, course.course_name) for course in Courses.objects.all()
        ]
        self.fields["session_year_id"].choices = [
            (session.id, session.display_name) for session in SessionYearModel.objects.all()
        ]


class StudentSearchForm(forms.Form):
    q = forms.CharField(
        label="Search students",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Name, username, email, address, course, or session",
        }),
    )
    course_id = forms.ModelChoiceField(
        label="Course",
        queryset=Courses.objects.none(),
        required=False,
        empty_label="All courses",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    session_year_id = forms.ModelChoiceField(
        label="Academic session",
        queryset=SessionYearModel.objects.none(),
        required=False,
        empty_label="All sessions",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    gender = forms.ChoiceField(
        label="Gender",
        required=False,
        choices=(("", "All genders"), ("Male", "Male"), ("Female", "Female")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_id"].queryset = Courses.objects.order_by("course_name")
        self.fields["course_id"].label_from_instance = lambda course: course.course_name
        self.fields["session_year_id"].queryset = SessionYearModel.objects.order_by(
            "-session_start_year",
        )
        self.fields["session_year_id"].label_from_instance = (
            lambda session: session.display_name
        )


class ProfilePhotoForm(forms.ModelForm):
    profile_photo = ProfileImageField(
        required=False,
        validators=[validate_profile_photo],
        widget=forms.FileInput(attrs={
            "class": "form-control-file",
            "accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp",
        }),
    )
    clear_photo = forms.BooleanField(
        label="Remove current profile photo",
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ("profile_photo",)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("clear_photo") and self.files.get("profile_photo"):
            raise forms.ValidationError(
                "Choose a new photo or remove the current photo, not both."
            )
        return cleaned_data


class ProfileDirectoryFilterForm(forms.Form):
    q = forms.CharField(
        label="Search",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Name, role, student ID, or staff ID",
        }),
    )
    role = forms.ChoiceField(
        label="Role",
        required=False,
        choices=(("", "All roles"), ("3", "Student"), ("2", "Staff / Teacher")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    course_id = forms.ModelChoiceField(
        label="Course / class",
        queryset=Courses.objects.none(),
        required=False,
        empty_label="All courses",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    subject_id = forms.ModelChoiceField(
        label="Subject",
        queryset=Subjects.objects.none(),
        required=False,
        empty_label="All subjects",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    session_year_id = forms.ModelChoiceField(
        label="Academic session",
        queryset=SessionYearModel.objects.none(),
        required=False,
        empty_label="All sessions",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, courses=None, subjects=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_id"].queryset = (
            courses if courses is not None else Courses.objects.order_by("course_name")
        )
        self.fields["subject_id"].queryset = (
            subjects if subjects is not None else Subjects.objects.order_by("subject_name")
        )
        self.fields["session_year_id"].queryset = SessionYearModel.objects.order_by(
            "-session_start_year",
        )