import json
import re
import PyPDF2
import pdfplumber
from typing import Dict, List, Optional, Any, Tuple
import spacy
from datetime import datetime
import logging
from dateutil import parser as date_parser


class ResumePDFParser:
    """
    An improved PDF resume parser that extracts structured information
    and returns it as JSON format.
    """

    def __init__(self):
        """Initialize the parser with required models and patterns."""
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning(
                "spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

        # Define section patterns with improved regex
        self.section_patterns = {
            'contact': [
                r'^contact\s*(information|details)?$',
                r'^personal\s*(details|information)?$',
                r'^details$'
            ],
            'summary': [
                r'^(professional|career|executive)\s+summary$',
                r'^summary$',
                r'^profile$',
                r'^(career\s+)?objective$',
                r'^about\s+me$'
            ],
            'experience': [
                r'^(work|professional|employment)\s+(experience|history)$',
                r'^experience$',
                r'^work\s+history$',
                r'^career\s+history$',
                r'^employment$'
            ],
            'education': [
                r'^education$',
                r'^(educational|academic)\s+(background|qualifications)$',
                r'^qualifications$',
                r'^degrees$'
            ],
            'skills': [
                r'^(technical\s+)?skills$',
                r'^core\s+competencies$',
                r'^competencies$',
                r'^technologies$',
                r'^expertise$',
                r'^technical\s+proficiency$'
            ],
            'projects': [
                r'^(key|notable|personal)\s+projects$',
                r'^project\s+(experience|portfolio)$',
                r'^projects$'
            ],
            'certifications': [
                r'^certifications$',
                r'^certificates$',
                r'^licenses$',
                r'^professional\s+certifications$'
            ],
            'achievements': [
                r'^(key\s+)?achievements$',
                r'^accomplishments$',
                r'^awards$',
                r'^honors$',
                r'^recognition$'
            ],
            'languages': [
                r'^languages$',
                r'^language\s+skills$'
            ]
        }

        # Improved patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        self.linkedin_pattern = r'(?:linkedin\.com\/in\/|linkedin\.com\/pub\/)[\w-]+'

        # Common skills keywords - expanded list
        self.technical_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'html', 'css', 'sql',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'fastapi',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'github', 'gitlab', 'jenkins',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'tensorflow',
            'pytorch', 'machine learning', 'data science', 'artificial intelligence',
            'celery', 'pytest', 'rest api', 'oauth', 'api integration', 'saas'
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using multiple methods for better accuracy.
        """
        text_content = ""

        try:
            # Method 1: Using pdfplumber (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"

            # Method 2: Fallback to PyPDF2 if pdfplumber fails
            if not text_content.strip():
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"

        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

        return text_content

    def extract_contact_information(self, text: str) -> Dict[str, Any]:
        """Extract contact information from text with improved accuracy and safe line-based parsing."""
        contact_info = {}

        # Extract email
        email_matches = re.findall(self.email_pattern, text, re.IGNORECASE)
        contact_info['email'] = email_matches[0] if email_matches else None

        # Extract phone numbers with better filtering
        phone_matches = re.finditer(self.phone_pattern, text)
        cleaned_phones = []
        for match in phone_matches:
            phone = match.group()
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            if 10 <= len(cleaned_phone) <= 15:
                cleaned_phones.append(phone.strip())
        contact_info['phone'] = cleaned_phones[0] if cleaned_phones else None

        # Extract name from first lines
        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        potential_names = []
        for line in lines[:10]:  # Check first 10 non-empty lines
            if (not re.search(r'resume|cv|curriculum|vitae|page|\d', line, re.IGNORECASE)
                    and 3 < len(line) < 50):
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.replace('.', '').replace('-', '').isalpha() for word in words):
                    potential_names.append(line)
                    break
        contact_info['name'] = potential_names[0] if potential_names else None

        # Extract LinkedIn profile
        # Accept both full URLs and handles following linkedin.com/in/
        linkedin_url_pattern = r'(https?://)?(www\.)?linkedin\.com/(in|pub)/[\w\-_/]+'
        linkedin_match = re.search(linkedin_url_pattern, text, re.IGNORECASE)
        if linkedin_match:
            linkedin = linkedin_match.group(0)
            if not linkedin.lower().startswith('http'):
                linkedin = 'https://' + linkedin
            contact_info['linkedin'] = linkedin
        else:
            contact_info['linkedin'] = None

        # Extract location by scanning single lines only to avoid multi-line false positives
        location = None
        for line in lines[:20]:
            if any(tok in line.lower() for tok in ['http', '@']):
                continue
            # Likely location if it has a comma and mostly words with letters
            if ',' in line and len(line) <= 60 and not re.search(r'\d{3,}', line):
                # Ensure both sides of comma look like words/cities
                parts = [p.strip() for p in line.split(',')]
                if 1 <= len(parts) <= 3 and all(re.match(r'^[A-Za-z .-]+$', p) for p in parts):
                    location = line
                    break
        contact_info['location'] = location

        return contact_info

    def extract_sections(self, text: str) -> Dict[str, List[str]]:
        """Extract different sections from the resume text with improved accuracy."""
        sections = {}
        lines = text.split('\n')
        current_section = 'general'
        sections[current_section] = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line is a section header (more strict matching)
            section_found = False
            line_lower = line.lower()

            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.fullmatch(pattern, line_lower, re.IGNORECASE):
                        current_section = section_name
                        sections[current_section] = []
                        section_found = True
                        break
                if section_found:
                    break

            if not section_found:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)

        return sections

    def extract_skills(self, text: str, sections: Dict[str, List[str]]) -> List[str]:
        """Extract skills from text and skills section with improved accuracy."""
        skills = set()

        # Extract from skills section if available
        if 'skills' in sections:
            skills_text = ' '.join(sections['skills']).lower()
            for skill in self.technical_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', skills_text, re.IGNORECASE):
                    skills.add(skill.title())

        # Extract from entire text
        text_lower = text.lower()
        for skill in self.technical_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower, re.IGNORECASE):
                skills.add(skill.title())

        # Extract from experience and projects sections too
        for section in ['experience', 'projects']:
            if section in sections:
                section_text = ' '.join(sections[section]).lower()
                for skill in self.technical_skills:
                    if re.search(r'\b' + re.escape(skill) + r'\b', section_text, re.IGNORECASE):
                        skills.add(skill.title())

        return sorted(list(skills))

    def _clean_languages(self, raw_languages: List[str]) -> List[str]:
        """Keep only real human languages and remove links or noise."""
        if not raw_languages:
            return []
        allowed_languages = {
            'english', 'urdu', 'hindi', 'arabic', 'french', 'german', 'spanish', 'chinese', 'mandarin',
            'punjabi', 'sindhi', 'pashto', 'balochi', 'bengali', 'turkish', 'russian', 'italian', 'japanese',
        }
        cleaned: List[str] = []
        for line in raw_languages:
            line_lower = line.lower().strip()
            if 'http' in line_lower or 'linkedin' in line_lower or '@' in line_lower:
                continue
            # Split by commas or pipes
            tokens = re.split(r'[|,/]+', line_lower)
            for token in tokens:
                token = token.strip()
                if token in allowed_languages and token.title() not in cleaned:
                    cleaned.append(token.title())
        return cleaned

    def _clean_projects(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove noise entries such as 'Skills:' pseudo-projects and empty fragments."""
        cleaned: List[Dict[str, Any]] = []
        skill_tokens = {
            'python', 'django', 'fastapi', 'flask', 'ml', 'machine learning', 'html', 'css', 'javascript',
            'back-end web development', 'backend', 'database', 'databases', 'django templates', 'pytest'
        }
        for proj in projects:
            name = (proj.get('name') or '').strip()
            if not name:
                continue
            name_lower = name.lower()
            if name_lower.startswith('skills') or name_lower in {'certification', 'certifications'}:
                continue
            # Remove projects that are obviously continuation fragments
            if len(name) <= 3 and not proj.get('description'):
                continue
            # Drop entries that are just skills/technologies without description
            if (name_lower in skill_tokens or name_lower.rstrip('.') in skill_tokens) and not (proj.get('description') or '').strip():
                continue
            # Normalize description whitespace
            if 'description' in proj and isinstance(proj['description'], str):
                proj['description'] = re.sub(r'\s+', ' ', proj['description']).strip()
            # Drop descriptions that are just "Skills:" noise
            if 'description' in proj and isinstance(proj['description'], str) and proj['description'].lower().startswith('skills:'):
                proj.pop('description', None)
            cleaned.append(proj)
        return cleaned

    def _merge_project_fragments(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge fragment-like project entries into their preceding project's description."""
        if not projects:
            return []
        merged: List[Dict[str, Any]] = []
        for proj in projects:
            name = (proj.get('name') or '').strip()
            desc = proj.get('description')
            is_fragment = (
                (not desc or not str(desc).strip()) and (
                    name.lower().startswith('the ') or
                    (name and name[0].islower()) or
                    len(name.split()) <= 4
                )
            )
            if merged and is_fragment:
                # Append fragment to previous project's description
                if 'description' not in merged[-1] or not merged[-1]['description']:
                    merged[-1]['description'] = name
                else:
                    if isinstance(merged[-1]['description'], list):
                        if not merged[-1]['description']:
                            merged[-1]['description'].append(name)
                        else:
                            merged[-1]['description'][-1] = (merged[-1]['description'][-1] + ' ' + name).strip()
                    else:
                        merged[-1]['description'] = (str(merged[-1]['description']) + ' ' + name).strip()
                continue
            merged.append(proj)
        return merged

    def _extract_certifications_from_text(self, text: str) -> List[str]:
        """Heuristically extract certification names from raw text."""
        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        certs: List[str] = []
        for line in lines:
            if re.search(r'certification|certificate|certifications', line, re.IGNORECASE):
                # Remove leading label like 'Certification:'
                clean = re.sub(r'(?i)^(certification|certificate|certifications)[:\-\s]*', '', line).strip()
                if clean and clean not in certs:
                    certs.append(clean)
        return certs

    def _improve_location(self, lines: List[str], current_location: Optional[str]) -> Optional[str]:
        """Infer a better location using strict location patterns and a known cities list."""
        if current_location and re.search(r'^[A-Za-z .-]+(?:,\s*[A-Za-z .-]+){0,2}$', current_location):
            return current_location

        known_cities = {
            'karachi', 'lahore', 'islamabad', 'Bahawalpur', 'rawalpindi', 'multan', 'peshawar',
            'dubai', 'riyadh', 'jeddah', 'london', 'new york', 'san francisco', 'seattle', 'berlin',
            'paris', 'madrid', 'rome', 'delhi', 'mumbai', 'bangalore', 'chennai'
        }
        known_regions = {'pakistan', 'india', 'uae', 'saudi arabia', 'united states', 'usa', 'uk'}

        # Try lines that have commas and only letters/spaces/dots/hyphens
        for line in lines[:80]:
            low = line.lower()
            if 'http' in low or '@' in low:
                continue
            # Search for substrings like "Xxx, Yyy" that only contain letters/spaces/dots/hyphens
            for match in re.finditer(r'([A-Za-z .-]{2,}?,\s*[A-Za-z .-]{2,})', line):
                candidate = match.group(1).strip(' .-')
                # Remove leading connectors like 'and', 'in', 'at', 'from'
                candidate = re.sub(r'^(?:and|in|at|from)\s+', '', candidate, flags=re.IGNORECASE).strip()
                tokens = [t.strip() for t in candidate.split(',') if t.strip()]
                token_lowers = [t.lower() for t in tokens]
                if any(t in known_cities for t in token_lowers) or any(t in known_regions for t in token_lowers):
                    return ', '.join(tokens)

        # Fallback: single token that matches known city
        for line in lines[:80]:
            low = line.lower().strip()
            if low in known_cities:
                return line.strip()

        return current_location or None

    def _normalize_experiences(self, experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize experience items to consistent keys and remove noise."""
        normalized: List[Dict[str, Any]] = []
        known_cities = {
            'karachi', 'lahore', 'islamabad', 'bahawalpur', 'rawalpindi', 'multan', 'peshawar',
            'dubai', 'riyadh', 'jeddah', 'london', 'new york', 'san francisco', 'seattle', 'berlin',
            'paris', 'madrid', 'rome', 'delhi', 'mumbai', 'bangalore', 'chennai'
        }
        known_regions = {'pakistan', 'india', 'uae', 'saudi arabia', 'united states', 'usa', 'uk'}
        for exp in experiences:
            title = (exp.get('title') or '').strip()
            company = (exp.get('company') or '').strip()
            duration = (exp.get('duration') or '').strip()
            description = exp.get('description') or []

            # Remove duration remnants from title/company
            title = re.sub(r'\b\d{1,2}/\d{4}\b.*$', '', title).strip(' -–—')
            company = re.sub(r'\b\d{1,2}/\d{4}\b.*$', '', company).strip(' -–—')

            # If title seems to include company with ' at ', split
            if not company and ' at ' in title.lower():
                parts = re.split(r'(?i)\s+at\s+', title, maxsplit=1)
                if len(parts) == 2:
                    title, company = parts[0].strip(), parts[1].strip()

            # If title is like "Role, Company" split on first comma
            if not company and ',' in title:
                left, right = title.split(',', 1)
                if 2 <= len(right.strip()) <= 120:
                    title, company = left.strip(), right.strip()

            # Ensure title no longer carries trailing ", Company"
            if ',' in title:
                possible_title, possible_tail = title.split(',', 1)
                if len(possible_title.split()) >= 1 and len(possible_tail.strip().split()) >= 1:
                    title = possible_title.strip()

            # Bound lengths to avoid whole paragraphs in fields
            if len(title) > 120:
                title = title[:120].rstrip()
            if len(company) > 120:
                company = company[:120].rstrip()

            # Ensure description is a list of strings and clean noise
            if isinstance(description, str):
                description = [description]
            cleaned_desc: List[str] = []
            for d in description:
                d = str(d).strip()
                if not d:
                    continue
                if d.lower().startswith('skills:'):
                    continue
                # Remove trailing ", City, Country" from description lines
                d = re.sub(r',\s*[A-Za-z .-]{2,},\s*[A-Za-z .-]{2,}$', '', d).strip()
                cleaned_desc.append(d)

            # If company looks like a sentence (contains action verbs), demote to description
            action_verbs = ['developed', 'designed', 'implemented', 'maintained', 'built', 'worked', 'led', 'optimized']
            if company and (len(company.split()) > 8 or any(v in company.lower() for v in action_verbs)):
                cleaned_desc.append(company)
                company = ''

            item: Dict[str, Any] = {}
            if title:
                item['title'] = title
            if company:
                item['company'] = company
            if duration:
                item['duration'] = duration
            if cleaned_desc:
                item['description'] = cleaned_desc

            # Keep only entries that have at least title or company
            if (item.get('title') or item.get('company')) and (item.get('company') or item.get('duration') or item.get('description')):
                normalized.append(item)

        return normalized

    def _compute_years_of_experience(self, experiences: List[Dict[str, Any]]) -> Optional[float]:
        """Compute total years of experience based on durations; fall back to None if unknown."""
        if not experiences:
            return None
        earliest_start: Optional[datetime] = None
        latest_end: Optional[datetime] = None
        now = datetime.now()

        def parse_duration(duration_str: str) -> Tuple[Optional[datetime], Optional[datetime]]:
            # Examples: "12/2024 – Present", "2023 - Present", "01/2023 - 06/2024"
            if not duration_str:
                return None, None
            parts = re.split(r'[-–—to]+', duration_str, flags=re.IGNORECASE)
            parts = [p.strip() for p in parts if p.strip()]
            start_dt: Optional[datetime] = None
            end_dt: Optional[datetime] = None
            if parts:
                try:
                    start_dt = date_parser.parse(parts[0], default=datetime(1900, 1, 1))
                except Exception:
                    start_dt = None
            if len(parts) >= 2:
                if re.search(r'present|current', parts[1], re.IGNORECASE):
                    end_dt = now
                else:
                    try:
                        end_dt = date_parser.parse(parts[1], default=datetime(1900, 1, 1))
                    except Exception:
                        end_dt = None
            return start_dt, end_dt

        for exp in experiences:
            duration = exp.get('duration')
            if not duration:
                continue
            start_dt, end_dt = parse_duration(duration)
            if start_dt and (earliest_start is None or start_dt < earliest_start):
                earliest_start = start_dt
            if end_dt is None:
                end_dt = now
            if end_dt and (latest_end is None or end_dt > latest_end):
                latest_end = end_dt

        if earliest_start and latest_end and latest_end > earliest_start:
            total_years = (latest_end - earliest_start).days / 365.25
            return round(total_years, 2)
        return None

    def extract_experience(self, sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract work experience ensuring only experience lines are parsed."""
        experiences = []

        if 'experience' not in sections:
            return experiences

        experience_text = sections['experience']
        current_job: Dict[str, Any] = {}
        bullet_points: List[str] = []

        # Patterns to identify job entries
        job_patterns = [
            r'^(.+?)\s+(\d{1,2}/\d{4}\s*[-–—]\s*(?:present|\d{1,2}/\d{4}))\s*(.*)$',
            r'^(.+?)\s+(\d{4}\s*[-–—]\s*(?:present|\d{4}))\s*(.*)$',
            r'^(.+?)\s+at\s+(.+?)\s+(\d{1,2}/\d{4}\s*[-–—]\s*(?:present|\d{1,2}/\d{4}))$',
            r'^(.+?)\s+at\s+(.+?)\s+(\d{4}\s*[-–—]\s*(?:present|\d{4}))$'
        ]

        for raw_line in experience_text:
            line = raw_line.strip()
            if not line or line in ['•', '·', '-']:
                continue

            # Ignore lines that look like section bleed-through
            if line.lower() in ['summary', 'skills', 'projects', 'education', 'certifications', 'achievements', 'languages']:
                continue

            is_new_job = False
            job_match = None
            for pattern in job_patterns:
                job_match = re.search(pattern, line, re.IGNORECASE)
                if job_match:
                    is_new_job = True
                    break

            # Also check for reasonable title-only lines
            if not is_new_job and len(line) < 100 and not line.startswith(('•', '·', '-')):
                title_keywords = ['developer', 'engineer', 'manager', 'analyst', 'specialist',
                                  'consultant', 'director', 'lead', 'architect', 'designer']
                if any(keyword in line.lower() for keyword in title_keywords):
                    is_new_job = True

            if is_new_job:
                if current_job:
                    if bullet_points:
                        current_job['description'] = bullet_points
                    experiences.append(current_job)
                    bullet_points = []

                current_job = {}
                if job_match:
                    groups = job_match.groups()
                    if len(groups) >= 2:
                        current_job['title'] = job_match.group(1).strip()
                        current_job['duration'] = job_match.group(2).strip()
                        if len(groups) >= 3 and job_match.group(3):
                            # If pattern captured a company field
                            maybe_company = job_match.group(3).strip()
                            # Avoid duration accidentally placed as company
                            if not re.search(r'\d{4}', maybe_company):
                                current_job['company'] = maybe_company
                else:
                    current_job['title'] = line

            elif line.startswith(('•', '·', '-')):
                clean_line = re.sub(r'^[•·\-]\s*', '', line)
                bullet_points.append(clean_line)
            elif current_job and 'company' not in current_job and len(line) < 100 and not re.search(r'\d{4}', line):
                current_job['company'] = line
            elif current_job and bullet_points:
                bullet_points[-1] += ' ' + line

        if current_job:
            if bullet_points:
                current_job['description'] = bullet_points
            experiences.append(current_job)

        return experiences

    def extract_education(self, sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract education information with improved parsing."""
        education = []

        if 'education' not in sections:
            return education

        education_text = sections['education']
        current_edu = {}
        collecting_description = False

        for line in education_text:
            line = line.strip()
            if not line:
                continue

            # Check for degree patterns
            degree_match = re.search(
                r'\b(bachelor|master|ph\.?d|doctorate|m\.?sc|b\.?sc|m\.?tech|b\.?tech|diploma|certificate|associate)\b',
                line, re.IGNORECASE
            )

            if degree_match:
                if current_edu:
                    education.append(current_edu)
                current_edu = {'degree': line}
                collecting_description = False
            elif current_edu and 'institution' not in current_edu:
                # Assume next non-empty line is institution if it doesn't contain dates
                if not re.search(r'\b(19|20)\d{2}\b', line):
                    current_edu['institution'] = line
            elif re.search(r'\b(19|20)\d{2}\b', line):
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    current_edu['year'] = year_match.group()
            elif current_edu:
                # Collect additional details
                if 'description' not in current_edu:
                    current_edu['description'] = []
                current_edu['description'].append(line)

        if current_edu:
            education.append(current_edu)

        return education

    def extract_experience(self, sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract work experience information with improved parsing for multiple experiences."""
        experiences = []

        if 'experience' not in sections:
            return experiences

        experience_text = sections['experience']
        current_job = {}
        bullet_points = []

        # Patterns to identify job entries
        job_patterns = [
            r'^(.+?)\s+(\d{1,2}/\d{4}\s*[-–—]\s*(?:present|\d{1,2}/\d{4}))\s*(.*)$',
            r'^(.+?)\s+(\d{4}\s*[-–—]\s*(?:present|\d{4}))\s*(.*)$',
            r'^(.+?)\s+at\s+(.+?)\s+(\d{1,2}/\d{4}\s*[-–—]\s*(?:present|\d{1,2}/\d{4}))$',
            r'^(.+?)\s+at\s+(.+?)\s+(\d{4}\s*[-–—]\s*(?:present|\d{4}))$'
        ]

        for line in experience_text:
            line = line.strip()

            # Skip empty lines and standalone bullet markers
            if not line or line in ['•', '·', '-']:
                continue

            # Check if this line starts a new job entry
            is_new_job = False
            job_match = None

            for pattern in job_patterns:
                job_match = re.search(pattern, line, re.IGNORECASE)
                if job_match:
                    is_new_job = True
                    break

            # Also check for lines that look like job titles without dates
            if not is_new_job and len(line) < 100 and not line.startswith(('•', '·', '-')):
                # Check if it contains job title keywords
                title_keywords = ['developer', 'engineer', 'manager', 'analyst', 'specialist',
                                  'consultant', 'director', 'lead', 'architect', 'designer']
                if any(keyword in line.lower() for keyword in title_keywords):
                    is_new_job = True

            if is_new_job:
                # Save previous job if exists
                if current_job:
                    if bullet_points:
                        current_job['description'] = bullet_points
                    experiences.append(current_job)
                    bullet_points = []

                # Create new job entry
                current_job = {}

                if job_match:
                    # Extract from pattern match
                    if len(job_match.groups()) >= 2:
                        current_job['title'] = job_match.group(1).strip()
                        current_job['duration'] = job_match.group(2).strip()

                        if len(job_match.groups()) >= 3 and job_match.group(3):
                            current_job['company'] = job_match.group(3).strip()
                else:
                    # Simple title-based detection
                    current_job['title'] = line

            elif line.startswith(('•', '·', '-')):
                # This is a bullet point
                clean_line = re.sub(r'^[•·\-]\s*', '', line)
                bullet_points.append(clean_line)
            elif current_job and 'company' not in current_job and len(line) < 100:
                # This might be the company name
                current_job['company'] = line
            elif current_job and bullet_points:
                # Continuation of the last bullet point
                if bullet_points:
                    bullet_points[-1] += ' ' + line

        # Add the last job
        if current_job:
            if bullet_points:
                current_job['description'] = bullet_points
            experiences.append(current_job)

        return experiences

    def extract_projects(self, sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract project information with improved parsing for multiple projects."""
        projects = []

        if 'projects' not in sections:
            return projects

        project_text = sections['projects']
        current_project = {}
        description_lines = []

        # Indicators of project titles
        project_indicators = [
            'project', 'ecommerce', 'website', 'application', 'system',
            'platform', 'dashboard', 'api', 'mobile', 'web'
        ]

        for line in project_text:
            line = line.strip()
            if not line:
                continue

            # Check if this line could be a project title
            is_project_title = (
                    len(line) < 80 and
                    not line.startswith(('•', '·', '-')) and
                    any(indicator in line.lower() for indicator in project_indicators) and
                    not re.search(r'[a-z][.!?]\s*[A-Z]', line)  # Not a sentence continuation
            )

            # Also check for lines that are clearly project names
            if not is_project_title and len(line) < 60:
                # Check if it's capitalized or has specific patterns
                words = line.split()
                if (len(words) <= 5 and
                        any(word.istitle() or word.isupper() for word in words) and
                        not any(word.lower() in ['the', 'and', 'with', 'for', 'using'] for word in words)):
                    is_project_title = True

            if is_project_title:
                # Save previous project if exists
                if current_project:
                    if description_lines:
                        current_project['description'] = ' '.join(description_lines)
                    projects.append(current_project)
                    description_lines = []

                # Create new project
                current_project = {'name': line}
            elif current_project:
                # This is part of the project description
                if line.startswith(('•', '·', '-')):
                    clean_line = re.sub(r'^[•·\-]\s*', '', line)
                    description_lines.append(clean_line)
                elif description_lines:
                    # Continue the last description line
                    description_lines[-1] += ' ' + line
                else:
                    description_lines.append(line)

        # Add the last project
        if current_project:
            if description_lines:
                current_project['description'] = ' '.join(description_lines)
            projects.append(current_project)

        return projects

    def parse_resume(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main method to parse resume PDF and return structured JSON data.
        """
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)

            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")

            # Extract sections
            sections = self.extract_sections(text)

            # Contact info first, then flatten to top-level keys
            contact = self.extract_contact_information(text)

            # Build structured flat resume data
            resume_data = {
                'name': contact.get('name'),
                'email': contact.get('email'),
                'phone': contact.get('phone'),
                'linkedin': contact.get('linkedin'),
                'location': contact.get('location'),
                'summary': ' '.join(sections.get('summary', [])),
                'skills': self.extract_skills(text, sections),
                'work_experience': self._normalize_experiences(self.extract_experience(sections)),
                'education': self.extract_education(sections),
                'projects': self._merge_project_fragments(self._clean_projects(self.extract_projects(sections))),
                'certifications': sections.get('certifications', []),
                'achievements': sections.get('achievements', []),
                'languages': sections.get('languages', []),
                'extraction_metadata': {
                    'extracted_at': datetime.now().isoformat(),
                    'total_sections_found': len(sections),
                    'text_length': len(text),
                    'success': True
                }
            }

            # Post-process cleanup
            all_lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
            resume_data['languages'] = self._clean_languages(resume_data['languages'])

            # Improve location if missing
            resume_data['location'] = self._improve_location(all_lines, resume_data.get('location'))

            # Pull certifications from text if empty
            if not resume_data['certifications']:
                resume_data['certifications'] = self._extract_certifications_from_text(text)

            # Compute years of experience
            resume_data['years_of_experience'] = self._compute_years_of_experience(resume_data['work_experience'])

            return resume_data

        except Exception as e:
            self.logger.error(f"Error parsing resume: {str(e)}")
            return {
                'error': str(e),
                'extraction_metadata': {
                    'extracted_at': datetime.now().isoformat(),
                    'success': False
                }
            }

    def parse_to_json(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Parse resume and return/save as JSON string.
        """
        resume_data = self.parse_resume(pdf_path)
        json_output = json.dumps(resume_data, indent=2, ensure_ascii=False)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_output)

        return json_output