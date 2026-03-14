from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from .models import JobDescription, Resume, ScreeningSession
from .resume_parser import ResumeParser
from .resume_scorer import ResumeScorer
import os

def home(request):
    """Home page with dashboard"""
    total_jobs = JobDescription.objects.count()
    total_resumes = Resume.objects.count()
    avg_match_score = Resume.objects.aggregate(Avg('match_score'))['match_score__avg'] or 0
    shortlisted = Resume.objects.filter(is_shortlisted=True).count()
    
    recent_jobs = JobDescription.objects.all()[:5]
    
    context = {
        'total_jobs': total_jobs,
        'total_resumes': total_resumes,
        'avg_match_score': round(avg_match_score, 2),
        'shortlisted': shortlisted,
        'recent_jobs': recent_jobs
    }
    return render(request, 'screener/home.html', context)


def create_job(request):
    """Create new job description"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        required_skills = request.POST.get('required_skills')
        experience_required = request.POST.get('experience_required')
        education_required = request.POST.get('education_required')
        
        job = JobDescription.objects.create(
            title=title,
            description=description,
            required_skills=required_skills,
            experience_required=experience_required,
            education_required=education_required
        )
        
        messages.success(request, 'Job description created successfully!')
        return redirect('job_detail', job_id=job.id)
    
    return render(request, 'screener/create_job.html')


def job_list(request):
    """List all job descriptions"""
    jobs = JobDescription.objects.all()
    return render(request, 'screener/job_list.html', {'jobs': jobs})


def job_detail(request, job_id):
    """Job description details with resume upload"""
    job = get_object_or_404(JobDescription, id=job_id)
    resumes = Resume.objects.filter(job_description=job).order_by('-match_score')
    
    if request.method == 'POST' and request.FILES.get('resume_file'):
        resume_file = request.FILES['resume_file']
        
        # Save resume
        resume = Resume.objects.create(
            job_description=job,
            resume_file=resume_file
        )
        
        # Parse and score resume
        try:
            file_path = resume.resume_file.path
            parser = ResumeParser(file_path)
            parsed_data = parser.parse()
            
            # Update resume with parsed data
            resume.candidate_name = parsed_data['name']
            resume.email = parsed_data['email']
            resume.phone = parsed_data['phone']
            resume.extracted_text = parsed_data['text']
            resume.extracted_skills = parsed_data['skills']
            resume.extracted_experience = parsed_data['experience']
            resume.extracted_education = parsed_data['education']
            
            # Score resume
            scorer = ResumeScorer()
            job_data = {
                'description': job.description,
                'required_skills': job.required_skills,
                'experience_required': job.experience_required,
                'education_required': job.education_required
            }
            
            scores = scorer.calculate_match_score(parsed_data, job_data)
            
            resume.match_score = scores['overall_score']
            resume.skills_match_score = scores['skills_score']
            resume.experience_match_score = scores['experience_score']
            resume.education_match_score = scores['education_score']
            
            # Auto-shortlist if score > 70
            if resume.match_score >= 70:
                resume.is_shortlisted = True
            
            resume.save()
            
            messages.success(request, f'Resume uploaded and analyzed! Match Score: {resume.match_score}%')
        
        except Exception as e:
            messages.error(request, f'Error processing resume: {str(e)}')
        
        return redirect('job_detail', job_id=job.id)
    
    context = {
        'job': job,
        'resumes': resumes,
        'total_resumes': resumes.count(),
        'shortlisted_count': resumes.filter(is_shortlisted=True).count()
    }
    
    return render(request, 'screener/job_detail.html', context)


def resume_detail(request, resume_id):
    """Detailed resume view"""
    resume = get_object_or_404(Resume, id=resume_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'shortlist':
            resume.is_shortlisted = True
            resume.save()
            messages.success(request, 'Resume shortlisted!')
        elif action == 'reject':
            resume.is_shortlisted = False
            resume.save()
            messages.info(request, 'Resume removed from shortlist')
        
        return redirect('resume_detail', resume_id=resume.id)
    
    return render(request, 'screener/resume_detail.html', {'resume': resume})


def analytics(request):
    """Analytics dashboard"""
    jobs = JobDescription.objects.annotate(
        resume_count=Count('resumes'),
        avg_score=Avg('resumes__match_score')
    )
    
    all_resumes = Resume.objects.all()
    
    # Score distribution
    score_ranges = {
        '90-100': all_resumes.filter(match_score__gte=90).count(),
        '80-89': all_resumes.filter(match_score__gte=80, match_score__lt=90).count(),
        '70-79': all_resumes.filter(match_score__gte=70, match_score__lt=80).count(),
        '60-69': all_resumes.filter(match_score__gte=60, match_score__lt=70).count(),
        'Below 60': all_resumes.filter(match_score__lt=60).count(),
    }
    
    context = {
        'jobs': jobs,
        'score_ranges': score_ranges,
        'total_resumes': all_resumes.count()
    }
    
    return render(request, 'screener/analytics.html', context)


def bulk_upload(request, job_id):
    """Bulk resume upload"""
    job = get_object_or_404(JobDescription, id=job_id)
    
    if request.method == 'POST':
        files = request.FILES.getlist('resume_files')
        
        processed = 0
        errors = 0
        
        for file in files:
            try:
                resume = Resume.objects.create(
                    job_description=job,
                    resume_file=file
                )
                
                # Parse and score
                parser = ResumeParser(resume.resume_file.path)
                parsed_data = parser.parse()
                
                resume.candidate_name = parsed_data['name']
                resume.email = parsed_data['email']
                resume.phone = parsed_data['phone']
                resume.extracted_text = parsed_data['text']
                resume.extracted_skills = parsed_data['skills']
                resume.extracted_experience = parsed_data['experience']
                resume.extracted_education = parsed_data['education']
                
                scorer = ResumeScorer()
                job_data = {
                    'description': job.description,
                    'required_skills': job.required_skills,
                    'experience_required': job.experience_required,
                    'education_required': job.education_required
                }
                
                scores = scorer.calculate_match_score(parsed_data, job_data)
                resume.match_score = scores['overall_score']
                resume.skills_match_score = scores['skills_score']
                resume.experience_match_score = scores['experience_score']
                resume.education_match_score = scores['education_score']
                
                if resume.match_score >= 70:
                    resume.is_shortlisted = True
                
                resume.save()
                processed += 1
                
            except Exception as e:
                errors += 1
                print(f"Error processing {file.name}: {e}")
        
        messages.success(request, f'Processed {processed} resumes successfully. {errors} errors.')
        return redirect('job_detail', job_id=job.id)
    
    return render(request, 'screener/bulk_upload.html', {'job': job})
