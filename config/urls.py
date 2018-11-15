from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Expressways Administration'
admin.site.site_title = 'Expressways Administration'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('expressways.core.urls', namespace='core')),
]
