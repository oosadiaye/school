from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/', include('students.urls')),
    path('api/academic/', include('academic.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/library/', include('library.urls')),
    path('api/hostel/', include('hostel.urls')),
    path('api/hr/', include('hr.urls')),
    path('api/nuc/', include('nuc.urls')),
    path('api/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
