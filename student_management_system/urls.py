from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from student_management_app import ProfileViews


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('student_management_app.urls')),
    path(
        f"{settings.MEDIA_URL.strip('/')}/<path:stored_path>",
        ProfileViews.secure_media_file,
        name="secure_media_file",
    ),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
