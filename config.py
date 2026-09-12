# ============================================================================
# NAUKRI JOB AUTOMATION - CONFIGURATION FILE
# ============================================================================
# This configuration file stores all settings for the Naukri job portal
# automation tool, including login credentials, search parameters, and
# job filtering rules.

import os
from pathlib import Path

# ============================================================================
# AUTHENTICATION CREDENTIALS
# ============================================================================
# Naukri.com login credentials. These are loaded from environment variables
# with fallback default values. In production, credentials should ONLY be
# stored in environment variables, not hardcoded here.

NAUKRI_USERNAME = os.getenv("NAUKRI_USERNAME", "ashishparte9298@gmail.com")
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD", "Parte@1234")

# ============================================================================
# JOB SEARCH PARAMETERS
# ============================================================================
# Define what jobs to search for and where to search

# The main keyword to search for on Naukri (e.g., "Automation manual api")
JOB_KEYWORD = os.getenv("NAUKRI_JOB_KEYWORD", "SDET Python Selenium, Senior SDET Python, SDET Automation Python, QA Automation Engineer Python, Senior QA Automation Engineer Python, Automation Test Engineer Python Selenium, Test Automation Engineer Selenium Python, SDET Playwright Python, API Automation Python, QA SDET Python, Senior Test Automation Engineer Python, Automation Engineer Selenium Python, Python Automation Tester, QA Automation Selenium Python, Test Automation Python PyTest")

# List of locations to filter job results. The comma-separated list from
# the environment variable is split and each location is stripped of whitespace
LOCATIONS = [
    location.strip()
    for location in os.getenv("NAUKRI_LOCATIONS", "Pune, Mumbai").split(",")
    if location.strip()
]

# Maximum number of pages to browse when searching for jobs
MAX_PAGES = int(os.getenv("NAUKRI_MAX_PAGES", "5"))

# Maximum number of times to scroll down on each page to load more job listings
MAX_SCROLLS = int(os.getenv("NAUKRI_MAX_SCROLLS", "2"))

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================
# Configure where scraped job data should be saved

# Directory path where job results will be exported
OUTPUT_FOLDER = Path(
    os.getenv("NAUKRI_OUTPUT_FOLDER", "/Users/ashishparte/Downloads/Job portal")
)

# Complete path to the Excel file where job data will be saved
OUTPUT_FILE = OUTPUT_FOLDER / "naukri_jobs1.xlsx"

# ============================================================================
# APPLICATION SCREENING QUESTIONS - AUTO-FILL ANSWERS
# ============================================================================
# Predefined answers for common screening questions during job applications.
# The automation tool uses these answers to auto-fill application forms.
# Keys are case-insensitive and matched against screening questions.

APPLICATION_ANSWERS = {
    # Experience-related questions (in years)
    "years of experience": "5",
    "total experience": "5",
    "relevant experience": "5",
    
    # Technical skills - Operating Systems
    "linux/unix operating system": "5",
    "linux/unix": "5",
    "linux": "5",
    "unix": "5",
    
    # Technical skills - Test Automation Tools
    "selenium experience": "5",
    "python experience": "5",
    "playwright": "Yes",
    "pytest": "Yes",
    
    # Testing Types
    "automation testing": "Yes",
    "manual testing": "Yes",
    "api testing": "Yes",
    "rest api": "Yes",
    
    # Database & Development Tools
    "sql": "Yes",
    "mysql": "Yes",
    "jira": "Yes",
    "git": "Yes",
    "jenkins": "Yes",
    
    # Location Preferences
    "current location": "Mumbai",
    "preferred location": "Mumbai, Pune",
    "willing to relocate": "Yes",
    
    # Notice Period
    "notice period": "15 days",
    "serving notice period": "Yes",
}

# ============================================================================
# SKIP APPLICATION STATUSES
# ============================================================================
# A set of job statuses that indicate the job should be skipped (not applied to).
# If a job has any of these statuses, the automation will mark it as processed
# but won't attempt to submit an application.

SKIP_STATUSES = {
    "applied",                              # Job has already been applied to
    "already applied",                      # Confirmation that application exists
    "submit",                               # Submit button not clearly available
    "submit/continue button not found",     # Unable to find submit button
    "apply button not found",               # Apply button could not be located
    "status unclear",                       # Job application status is ambiguous
    "error",                                # Error occurred during application
}

# ============================================================================
# RELEVANT JOB TITLE KEYWORDS
# ============================================================================
# Keywords to match against job titles to identify relevant QA/Testing positions.
# Jobs with titles containing any of these keywords will be prioritized for
# application. The matching is case-insensitive.

RELEVANT_TITLE_KEYWORDS = [
    # SDET (Software Development Engineer in Test) roles
"Automation Testing", "Selenium", "Automation", "Pytest",
    "sdet",
    "software development engineer in test",
    "software development engineer test",
    
    # General Automation Testing roles
    "automation test",
    "test automation",
    "automation testing",
    "automation engineer",
    "automation tester",
    "automation test engineer",
    "automation testing engineer",
    
    # QA roles (broad)
    "qa",
    "qa automation",
    "qa engineer",
    "qa tester",
    "qa analyst",
    "qa specialist",
    "quality automation",
    "quality assurance engineer",
    "quality assurance tester",
    "quality analyst",
    "quality engineer",
    "quality specialist",
    
    # Manual Testing roles
    "manual",
    "manual tester",
    "manual testing",
    "manual test",
    
    # API Testing roles
    "api",
    "api tester",
    "api testing",
    "api test engineer",
    
    # Test Tools/Frameworks (Selenium, Playwright, etc.)
    "selenium",
    "playwright",
    
    # General Testing Engineer roles
    "test engineer",
    "testing engineer",
    "test specialist",
    "testing specialist",
    "software test engineer",
    "software testing engineer",
    "software test analyst",
    "software tester",
    
    # Test Analyst roles
    "test analyst",
    "testing analyst",
    
    # Functional Testing roles
    "functional tester",
    "functional testing",
    "functional test engineer",
]

# ============================================================================
# EXCLUSION JOB TITLE KEYWORDS
# ============================================================================
# Keywords that indicate a job should be excluded from consideration.
# Jobs with titles containing any of these keywords will be skipped, even if
# they match the search criteria. This prevents applying to irrelevant roles
# like developer positions, support roles, or non-technical positions.

EXCLUSION_TITLE_KEYWORDS = [
    # Developer roles (not testing-focused)
    "frontend developer",
    "front end developer",
    "backend developer",
    "back end developer",
    "full stack developer",
    "fullstack developer",
    "software developer",
    "application developer",
    "java developer",
    "python developer",
    "ui developer",
    "mobile developer",
    "android developer",
    "ios developer",
    
    # Data roles (not testing-focused)
    "data engineer",
    "data scientist",
    "data analyst",
    
    # Infrastructure/Operations roles
    "devops engineer",
    "cloud engineer",
    "network engineer",
    "network administrator",
    "system administrator",
    
    # Business/Management roles
    "business analyst",
    "product manager",
    "project manager",
    
    # Support roles
    "technical support",
    "customer support",
    
    # Non-technical roles
    "sales",
    "marketing",
    
    # Design roles
    "ux designer",
]
