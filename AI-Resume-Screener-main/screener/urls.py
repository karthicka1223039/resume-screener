from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-job/', views.create_job, name='create_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('resume/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('analytics/', views.analytics, name='analytics'),
    path('job/<int:job_id>/bulk-upload/', views.bulk_upload, name='bulk_upload'),
]
