from django.urls import path

from expressways.core.views import HomeView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
