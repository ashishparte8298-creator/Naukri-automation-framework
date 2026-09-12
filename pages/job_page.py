# ============================================================================
# JOB PAGE - JOB APPLICATION HANDLING
# ============================================================================
# Handles the job application process on individual job pages:
# - Opening job pages
# - Finding and clicking apply buttons
# - Checking application status (already applied, applied, errors)
# - Submitting applications
# - Coordinating with chatbot for screening questions

import re
import time

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, log


class JobPage(BasePage):
    """Handles job application logic for individual job pages."""
    
    def open_job(self, url):
        """
        Open a job posting page and close any popups.
        
        Args:
            url: Direct URL to job posting
        """
        self.driver.get(url)
        time.sleep(5)
        self.close_common_popups()

    def find_apply_button(self):
        """
        Find the Apply button on the job page.
        Tries multiple selectors for different page layouts.
        
        Returns:
            WebElement: Apply button element, or None if not found
        """
        return self.find_visible_element(
            [
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'apply')]",
                ),
                (
                    By.XPATH,
                    "//a[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'apply')]",
                ),
                (
                    By.XPATH,
                    "//*[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'apply now')]",
                ),
            ],
            10,
        )

    def click_apply(self):
        """
        Find and click the Apply button.
        
        Returns:
            bool: True if apply button found and clicked, False otherwise
        """
        apply_button = self.find_apply_button()

        if apply_button is None:
            return False

        self.click_element(apply_button)
        log("Apply clicked.")
        time.sleep(1)
        return True

    def is_already_applied(self):
        """
        Check if user has already applied to this job.
        Searches for common "already applied" phrases in page text.
        
        Returns:
            bool: True if already applied message detected
        """
        body_text = self.visible_body_text()
        phrases = [
            "you have already applied",
            "application already submitted",
            "already applied",
        ]

        for phrase in phrases:
            if phrase in body_text:
                log(f"Already applied detected: {phrase}")
                return True

        return False

    def applied_keyword_found(self):
        """
        Check if 'applied' keyword appears on the page.
        Uses regex to find word boundary to avoid false matches.
        
        Returns:
            bool: True if 'applied' word found in page text
        """
        body_text = self.visible_body_text()
        return bool(re.search(r"\bapplied\b", body_text))

    def application_successful(self):
        """
        Check for success messages indicating application was submitted.
        Looks for various success phrase variations.
        
        Returns:
            bool: True if application success message detected
        """
        body_text = self.visible_body_text()
        phrases = [
            "application submitted",
            "application successful",
            "your application was successful",
            "successfully submitted",
            "your application has been submitted",
            "applied successfully",
            "application sent",
        ]
        return any(phrase in body_text for phrase in phrases)

    def submit_application(self):
        """
        Find and click the Submit or Continue button to submit application.
        Used after filling screening questions.
        
        Returns:
            bool: True if submit button found and clicked, False otherwise
        """
        button = self.find_visible_element(
            [
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'submit')]",
                ),
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'continue')]",
                ),
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'send application')]",
                ),
                (By.XPATH, "//input[@type='submit']"),
            ],
            5,
        )

        if button is None:
            return False

        try:
            self.click_element(button)
            log("Submit/Continue clicked.")
            time.sleep(2)
            return True
        except Exception as error:
            log("Submit error:", error)
            return False

    def apply_job(self, chatbot_page):
        """
        Main job application flow:
        1. Check if already applied
        2. Click apply button
        3. Check for immediate success
        4. Answer chatbot screening questions if present
        5. Submit application
        6. Verify success status
        
        Args:
            chatbot_page: ChatbotPage instance to handle screening questions
            
        Returns:
            str: Application result status (Applied, Already Applied, Apply Button Not Found, etc.)
        """
        # Check if already applied before clicking
        if self.is_already_applied():
            return "Already Applied"

        # Try to click Apply button
        if not self.click_apply():
            if self.is_already_applied():
                return "Already Applied"
            return "Apply Button Not Found"

        # Check if application was immediate/instant
        if self.applied_keyword_found() or self.application_successful():
            return "Applied"

        time.sleep(2)

        # Handle chatbot screening questions if present
        if chatbot_page.is_present():
            if chatbot_page.answer_until_success(self):
                return "Applied"

            # Try to submit after chatbot answers questions
            if self.submit_application():
                if self.application_successful() or self.applied_keyword_found():
                    return "Applied"

                if self.is_already_applied():
                    return "Already Applied"

                return "Status Unclear"

            return "Submit"

        # No chatbot, just check for success
        if self.application_successful() or self.applied_keyword_found():
            return "Applied"

        if self.is_already_applied():
            return "Already Applied"

        return "Status Unclear"
