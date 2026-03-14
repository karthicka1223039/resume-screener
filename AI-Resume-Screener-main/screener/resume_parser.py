import PyPDF2
import docx
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    print("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

class ResumeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = ""
        
    def extract_text(self):
        """Extract text from PDF or DOCX files"""
        if self.file_path.endswith('.pdf'):
            return self._extract_from_pdf()
        elif self.file_path.endswith('.docx') or self.file_path.endswith('.doc'):
            return self._extract_from_docx()
        else:
            return ""
    
    def _extract_from_pdf(self):
        """Extract text from PDF"""
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def _extract_from_docx(self):
        """Extract text from DOCX"""
        try:
            doc = docx.Document(self.file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
    
    def extract_name(self, text):
        """Extract candidate name using NER"""
        if nlp:
            doc = nlp(text[:500])  # Check first 500 characters
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text
        
        # Fallback: Extract first line as name
        lines = text.split('\n')
        for line in lines:
            if line.strip() and len(line.strip()) < 50:
                return line.strip()
        return "Unknown"
    
    def extract_email(self, text):
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def extract_phone(self, text):
        """Extract phone number"""
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else ""
    
    def extract_skills(self, text):
        """Extract skills from resume"""
        # Common technical skills list
        skills_list = [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'django', 'flask', 'react', 'angular', 'vue', 'node', 'express',
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'ai',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'html', 'css', 'bootstrap', 'tailwind', 'sass',
            'rest api', 'graphql', 'microservices', 'agile', 'scrum',
            'data analysis', 'data science', 'statistics', 'excel', 'tableau', 'power bi'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_list:
            if skill in text_lower:
                found_skills.append(skill)
        
        return ', '.join(set(found_skills))
    
    def extract_experience(self, text):
        """Extract work experience"""
        experience_keywords = ['experience', 'work history', 'employment', 'professional experience']
        education_keywords = ['education', 'academic', 'qualification']
        
        text_lower = text.lower()
        experience_section = ""
        
        for keyword in experience_keywords:
            if keyword in text_lower:
                start_idx = text_lower.index(keyword)
                # Find end of section (next major heading or education section)
                end_idx = len(text)
                for edu_keyword in education_keywords:
                    if edu_keyword in text_lower[start_idx:]:
                        end_idx = start_idx + text_lower[start_idx:].index(edu_keyword)
                        break
                
                experience_section = text[start_idx:end_idx]
                break
        
        return experience_section[:500] if experience_section else "Not specified"
    
    def extract_education(self, text):
        """Extract education details"""
        education_keywords = ['education', 'academic', 'qualification', 'university', 'college', 'degree']
        
        text_lower = text.lower()
        education_section = ""
        
        for keyword in education_keywords:
            if keyword in text_lower:
                start_idx = text_lower.index(keyword)
                education_section = text[start_idx:start_idx + 500]
                break
        
        # Extract degree types
        degrees = ['b.tech', 'btech', 'm.tech', 'mtech', 'bca', 'mca', 'bsc', 'msc', 
                   'ba', 'ma', 'phd', 'bachelor', 'master', 'diploma']
        
        found_degrees = []
        for degree in degrees:
            if degree in text_lower:
                found_degrees.append(degree.upper())
        
        return education_section if education_section else ', '.join(set(found_degrees))
    
    def parse(self):
        """Main parsing method"""
        self.text = self.extract_text()
        
        return {
            'text': self.text,
            'name': self.extract_name(self.text),
            'email': self.extract_email(self.text),
            'phone': self.extract_phone(self.text),
            'skills': self.extract_skills(self.text),
            'experience': self.extract_experience(self.text),
            'education': self.extract_education(self.text)
        }
