from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class ResumeScorer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def calculate_match_score(self, resume_data, job_description_data):
        """Calculate overall match score between resume and job description"""
        
        # Text similarity score (TF-IDF)
        text_score = self._calculate_text_similarity(
            resume_data['text'], 
            job_description_data['description']
        )
        
        # Skills match score
        skills_score = self._calculate_skills_match(
            resume_data['skills'], 
            job_description_data['required_skills']
        )
        
        # Experience match score
        experience_score = self._calculate_experience_match(
            resume_data['experience'], 
            job_description_data['experience_required']
        )
        
        # Education match score
        education_score = self._calculate_education_match(
            resume_data['education'], 
            job_description_data['education_required']
        )
        
        # Weighted overall score
        overall_score = (
            text_score * 0.3 +
            skills_score * 0.4 +
            experience_score * 0.2 +
            education_score * 0.1
        )
        
        return {
            'overall_score': round(overall_score * 100, 2),
            'text_score': round(text_score * 100, 2),
            'skills_score': round(skills_score * 100, 2),
            'experience_score': round(experience_score * 100, 2),
            'education_score': round(education_score * 100, 2)
        }
    
    def _calculate_text_similarity(self, resume_text, job_description):
        """Calculate cosine similarity using TF-IDF"""
        try:
            documents = [resume_text, job_description]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except:
            return 0.0
    
    def _calculate_skills_match(self, resume_skills, required_skills):
        """Calculate skills match percentage"""
        if not resume_skills or not required_skills:
            return 0.0
        
        resume_skills_list = [s.strip().lower() for s in resume_skills.split(',')]
        required_skills_list = [s.strip().lower() for s in required_skills.split(',')]
        
        matched_skills = set(resume_skills_list) & set(required_skills_list)
        
        if not required_skills_list:
            return 0.0
        
        return len(matched_skills) / len(required_skills_list)
    
    def _calculate_experience_match(self, resume_experience, required_experience):
        """Calculate experience match"""
        if not resume_experience or not required_experience:
            return 0.5
        
        # Extract years from text
        resume_years = self._extract_years(resume_experience)
        required_years = self._extract_years(required_experience)
        
        if resume_years >= required_years:
            return 1.0
        elif resume_years >= required_years * 0.7:
            return 0.8
        elif resume_years >= required_years * 0.5:
            return 0.6
        else:
            return 0.3
    
    def _calculate_education_match(self, resume_education, required_education):
        """Calculate education match"""
        if not resume_education or not required_education:
            return 0.5
        
        resume_education_lower = resume_education.lower()
        required_education_lower = required_education.lower()
        
        # Check for degree match
        if required_education_lower in resume_education_lower:
            return 1.0
        
        # Partial match
        keywords = required_education_lower.split()
        matches = sum(1 for keyword in keywords if keyword in resume_education_lower)
        
        return matches / len(keywords) if keywords else 0.5
    
    def _extract_years(self, text):
        """Extract years of experience from text"""
        # Look for patterns like "5 years", "5+ years", "5-7 years"
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*\d+\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
