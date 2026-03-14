from django.db import models
from django.utils import timezone

class JobDescription(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma-separated skills")
    experience_required = models.CharField(max_length=100)
    education_required = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class Resume(models.Model):
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='resumes')
    candidate_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    
    # Extracted information
    extracted_text = models.TextField(blank=True)
    extracted_skills = models.TextField(blank=True)
    extracted_experience = models.TextField(blank=True)
    extracted_education = models.TextField(blank=True)
    
    # Scoring
    match_score = models.FloatField(default=0.0)
    skills_match_score = models.FloatField(default=0.0)
    experience_match_score = models.FloatField(default=0.0)
    education_match_score = models.FloatField(default=0.0)
    
    uploaded_at = models.DateTimeField(default=timezone.now)
    is_shortlisted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.candidate_name} - {self.job_description.title}"
    
    class Meta:
        ordering = ['-match_score']


class ScreeningSession(models.Model):
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    session_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    total_resumes = models.IntegerField(default=0)
    shortlisted_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.session_name} - {self.job_description.title}"
    
    class Meta:
        ordering = ['-created_at']
