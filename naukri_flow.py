# ============================================================================
# NAUKRI JOB APPLICATION FLOW - MAIN ORCHESTRATOR
# ============================================================================
# Orchestrates the entire job application workflow on Naukri:
# 1. Fetch jobs matching criteria from search results
# 2. Store and filter jobs in Excel based on relevance
# 3. Auto-apply to relevant jobs with screening question answers
# 4. Generate summary report of application results

import sys
import time

from Naukari.config import (
    LOCATIONS,
    MAX_PAGES,
    NAUKRI_PASSWORD,
    NAUKRI_USERNAME,
    SKIP_STATUSES,
)
from Naukari.pages.chatbot_page import ChatbotPage
from Naukari.pages.job_page import JobPage
from Naukari.pages.login_page import LoginPage
from Naukari.pages.search_page import SearchPage
from Naukari.utils.excel_utils import ExcelJobsRepository


def log(message):
    """Print message with immediate flush to ensure real-time output."""
    print(message, flush=True)
    sys.stdout.flush()


class NaukriApplicationFlow:
    """Main orchestrator for the Naukri job application automation."""
    
    def __init__(self, driver, excel_repository=None):
        """
        Initialize the application flow with page objects and Excel repository.
        
        Args:
            driver: Selenium WebDriver instance
            excel_repository: Optional custom ExcelJobsRepository (for testing)
        """
        self.driver = driver
        self.excel = excel_repository or ExcelJobsRepository()
        self.login_page = LoginPage(driver)
        self.search_page = SearchPage(driver)
        self.job_page = JobPage(driver)
        self.chatbot_page = ChatbotPage(driver)

    def run(self):
        """
        Execute the complete job application flow:
        1. Prepare Excel file
        2. Fetch new jobs from search
        3. Filter relevant jobs
        4. Login and apply to jobs
        5. Return summary
        """
        self.excel.create_if_required()
        new_jobs = self.fetch_jobs()
        inserted = self.excel.save_new_jobs(new_jobs)
        kept, removed = self.excel.filter_irrelevant_jobs()
        jobs = self.excel.load_jobs()

        log(f"New jobs fetched this run: {len(new_jobs)}")
        log(f"New records inserted into Excel: {inserted}")
        log(f"Relevant jobs kept: {kept}")
        log(f"Irrelevant jobs removed: {removed}")
        log(f"Relevant jobs available in Excel: {len(jobs)}")

        if not jobs:
            log("No relevant jobs available in Excel.")
            return self.summary(len(new_jobs))

        # Login to Naukri and start applying
        self.login_page.login(NAUKRI_USERNAME, NAUKRI_PASSWORD)
        time.sleep(5)
        self.apply_jobs()
        return self.summary(len(new_jobs))

    def fetch_jobs(self):
        """
        Search for jobs across all configured locations and pages.
        Extracts job details (title, company, location, URL) from search results.
        
        Returns:
            list: List of job dictionaries with extracted job information
        """
        new_jobs = []

        for location in LOCATIONS:
            try:
                # Search for jobs in this location
                if not self.search_page.search(location):
                    log(f"No jobs found for {location}")
                    continue

                # Browse through pages and extract jobs
                for page in range(1, MAX_PAGES + 1):
                    log(f"{location} - PAGE {page}")
                    self.search_page.scroll_page()
                    new_jobs.extend(self.search_page.extract_jobs(location))

                    # Stop if next page doesn't exist
                    if page < MAX_PAGES and not self.search_page.go_to_next_page():
                        break

            except Exception as error:
                log(f"Error processing {location}: {error}")

        return new_jobs

    def apply_jobs(self):
        """
        Load jobs from Excel and attempt to apply to each one.
        Skips jobs with statuses indicating they've been applied or have errors.
        Updates Excel with application result after each job.
        """
        jobs = self.excel.load_jobs()
        total = len(jobs)

        for index, job in enumerate(jobs, start=1):
            status = job["status"].strip().lower()

            log("=" * 60)
            log(f"JOB {index}/{total}")
            log(f"Title    : {job['title']}")
            log(f"Company  : {job['company']}")
            log(f"Location : {job['location']}")
            log(f"Job URL  : {job['url']}")
            log(f"Excel Status : {job['status']}")
            log("=" * 60)

            # Skip jobs that have been processed or have errors
            if status in SKIP_STATUSES:
                log(f"SKIPPED - Excel status is '{job['status']}'")
                continue

            try:
                # Open job page and attempt to apply
                log("Opening job...")
                self.job_page.open_job(job["url"])
                result = self.job_page.apply_job(self.chatbot_page)
                self.excel.update_status(job, result)
                # Format result in uppercase for visibility
                formatted_result = result.upper().replace(" ", "_")
                log(formatted_result)
            except Exception as error:
                log("Application error:", error)
                self.excel.update_status(job, "Error")

            time.sleep(2)

    def summary(self, new_jobs_count=0):
        """
        Generate and print a summary report of all application attempts.
        Counts applications by status (applied, already applied, errors, etc.)
        
        Args:
            new_jobs_count: Number of new jobs fetched in this run (optional)
        
        Returns:
            dict: Dictionary with counts of each application status
        """
        jobs = self.excel.load_jobs()
        counts = {
            "applied": 0,
            "already_applied": 0,
            "button_missing": 0,
            "submit_missing": 0,
            "unclear": 0,
            "errors": 0,
        }

        # Count jobs by their status
        for job in jobs:
            status = job["status"].strip().lower()

            if status == "applied":
                counts["applied"] += 1
            elif status == "already applied":
                counts["already_applied"] += 1
            elif status == "apply button not found":
                counts["button_missing"] += 1
            elif status == "submit":
                counts["submit_missing"] += 1
            elif status == "status unclear":
                counts["unclear"] += 1
            elif status == "error":
                counts["errors"] += 1

        # Print final summary with better formatting
        log("=" * 60)
        log("FINAL SUMMARY")
        log("=" * 60)
        log(f"New Jobs Fetched        : {new_jobs_count}")
        log(f"Total Relevant Jobs     : {len(jobs)}")
        log(f"Applied                 : {counts['applied']}")
        log(f"Already Applied         : {counts['already_applied']}")
        log(f"Apply Button Missing    : {counts['button_missing']}")
        log(f"Submit/Continue Missing : {counts['submit_missing']}")
        log(f"Status Unclear          : {counts['unclear']}")
        log(f"Errors                  : {counts['errors']}")

        return counts
