from django.urls import path
from django.conf.urls import handler404, handler500

from expressways.core.views import (HomeView,
                                    DeleteOccurrenceConfiguration,
                                    CalculateView,
                                    ResultView,
                                    RoadSelectionView)

app_name = 'core'
urlpatterns = [
    path('', RoadSelectionView.as_view(), name='road'),
    path('home/<int:road_id>', HomeView.as_view(), name='home'),
    path('delete/<int:pk>', DeleteOccurrenceConfiguration.as_view(), name='delete'),
    path('calculate', CalculateView.as_view(), name='calculate'),
    path('result/<str:task_id>', ResultView.as_view(), name='result'),
]

handler404 = 'core.views.custom404'
handler500 = 'core.views.custom500'