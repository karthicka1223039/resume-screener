from django.contrib import admin
from .models import JobDescription, Resume, ScreeningSession

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'experience_required', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['created_at']

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['candidate_name', 'job_description', 'match_score', 'is_shortlisted', 'uploaded_at']
    list_filter = ['is_shortlisted', 'uploaded_at']
    search_fields = ['candidate_name', 'email']
    ordering = ['-match_score']

@admin.register(ScreeningSession)
class ScreeningSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'job_description', 'total_resumes', 'shortlisted_count', 'created_at']
    list_filter = ['created_at']
