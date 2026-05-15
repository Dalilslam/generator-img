from django.urls import path
from . import views

urlpatterns = [
    path('analytics/metrics/', views.AnalyticsMetricsView.as_view(), name='analytics-metrics'),
]