from django.urls import path

from expressways.core.views import (HomeView,
                                    NewOccurrenceConfiguration,
                                    DeleteOccurrenceConfiguration,
                                    CalculateView)

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new', NewOccurrenceConfiguration.as_view(), name='new'),
    path('delete/<int:pk>', DeleteOccurrenceConfiguration.as_view(), name='delete'),
    path('calculate', CalculateView.as_view(), name='calculate'),
]
