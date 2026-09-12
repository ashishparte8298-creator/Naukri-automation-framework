# ============================================================================
# CHATBOT PAGE - SCREENING QUESTION AUTO-ANSWERING
# ============================================================================
# Handles interaction with Naukri's screening chatbot:
# - Detecting chatbot presence on job application pages
# - Extracting chatbot questions and input fields
# - Auto-answering questions based on predefined configuration
# - Clicking Next/Continue/Submit buttons
# - Managing multiple rounds of questions

import time

from selenium.webdriver.common.by import By

from config import APPLICATION_ANSWERS
from pages.base_page import BasePage, log

class ChatbotPage(BasePage):
    """Handles interaction with Naukri screening chatbot."""
    
    # CSS and XPath selectors for chatbot question items (different variations)
    CHATBOT_SELECTORS = [
        (By.CSS_SELECTOR, ".botItem"),
        (By.CSS_SELECTOR, ".chatbot_ListItem"),
        (
            By.XPATH,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' botItem ')]",
        ),
        (
            By.XPATH,
            "//*[contains(concat(' ', normalize-space(@class), ' '), "
            "' chatbot_ListItem ')]",
        ),
    ]

    def is_present(self):
        """
        Check if chatbot is present on the page.
        
        Returns:
            bool: True if chatbot items are visible, False otherwise
        """
        return len(self.visible_items()) > 0

    def visible_items(self):
        """
        Get all visible chatbot question/input items on the page.
        Deduplicates items by text to avoid processing same question twice.
        
        Returns:
            list: List of visible WebElement chatbot items
        """
        items = []
        seen = set()

        for locator in self.CHATBOT_SELECTORS:
            try:
                for element in self.driver.find_elements(*locator):
                    try:
                        if not element.is_displayed():
                            continue

                        text = element.text.strip()
                        if text and text.lower() not in seen:
                            seen.add(text.lower())
                            items.append(element)
                    except Exception:
                        continue
            except Exception:
                continue

        return items

    def answer_until_success(self, job_page, max_rounds=30):
        """
        Repeatedly answer chatbot questions until application succeeds or max rounds reached.
        Handles multiple rounds of questions, clicking Next/Continue buttons between rounds.
        
        Args:
            job_page: JobPage instance to check for application success
            max_rounds: Maximum number of answer attempts (default: 30)
            
        Returns:
            bool: True if application succeeded, False otherwise
        """
        answered_keys = set()  # Track already-answered questions to avoid loops

        for round_no in range(1, max_rounds + 1):
            log(f"CHATBOT ROUND {round_no}")

            # Check if application already succeeded
            if job_page.application_successful():
                return True

            items = self.visible_items()
            log(f"Chatbot questions/items currently visible: {len(items)}")

            if not items:
                time.sleep(2)

                if job_page.application_successful():
                    return True

                # If no items and chatbot not present, exit loop
                if not self.is_present():
                    return False

                continue

            progress = False
            # Try to answer each visible question
            for item in items:
                question = self._question(item)

                if not question:
                    continue

                field = self._input(item)
                current_value = ""

                if field is not None:
                    try:
                        current_value = (field.get_attribute("value") or "").strip()
                    except Exception:
                        pass

                # Skip if we've already answered this exact question+value combo
                question_key = question.lower() + "|" + current_value
                if question_key in answered_keys:
                    continue

                if self._answer_item(item, question):
                    answered_keys.add(question_key)
                    progress = True
                    time.sleep(0.5)

            # Check success after answering questions
            if job_page.application_successful():
                return True

            # Try to click Next/Continue/Submit button
            if self.click_next_continue_or_submit():
                time.sleep(1.5)
                continue

            # If made progress, wait and try again
            if progress:
                time.sleep(2)
                continue

            time.sleep(2)

        return job_page.application_successful()

    def click_next_continue_or_submit(self):
        """
        Find and click Next, Continue, or Submit button in chatbot.
        Used to proceed to next set of questions.
        
        Returns:
            bool: True if button found and clicked, False otherwise
        """
        selectors = [
            (
                By.XPATH,
                "//button[contains(translate(normalize-space(.),"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'next')]",
            ),
            (
                By.XPATH,
                "//button[contains(translate(normalize-space(.),"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'continue')]",
            ),
            (
                By.XPATH,
                "//button[contains(translate(normalize-space(.),"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]",
            ),
            (
                By.XPATH,
                "//button[contains(translate(normalize-space(.),"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'send application')]",
            ),
            (By.XPATH, "//input[@type='submit']"),
        ]

        for locator in selectors:
            try:
                for button in self.driver.find_elements(*locator):
                    try:
                        if button.is_displayed() and button.is_enabled():
                            self.click_element(button)
                            log("Chatbot Next/Continue/Submit clicked.")
                            return True
                    except Exception:
                        continue
            except Exception:
                continue

        return False

    def _answer_item(self, item, question):
        """
        Answer a single chatbot question by finding the configured answer and entering it.
        
        Args:
            item: Chatbot question item WebElement
            question: Question text
            
        Returns:
            bool: True if answer successfully entered, False otherwise
        """
        log("CHATBOT QUESTION:")
        log(question)

        answer = self._answer_for(question)
        if answer is None:
            log("No configured answer for this question.")
            return False

        field = self._input(item)
        if field is None:
            log("Input field not found.")
            return False

        try:
            self.click_element(field)
            field.clear()
            field.send_keys(str(answer))
            log(f"ANSWER ENTERED: {answer}")
            return True
        except Exception as error:
            log("Unable to enter answer:", error)
            return False

    def _answer_for(self, question):
        """
        Find configured answer for a question.
        Matches question text against APPLICATION_ANSWERS keys.
        
        Args:
            question: Question text to search for
            
        Returns:
            str: Answer value from config, or None if no match
        """
        question = question.lower()

        for key, answer in APPLICATION_ANSWERS.items():
            if key in question:
                return answer

        return None

    def _question(self, item):
        """
        Extract question text from a chatbot item.
        
        Args:
            item: Chatbot item WebElement
            
        Returns:
            str: Question text, or empty string if error
        """
        try:
            return item.text.strip()
        except Exception:
            return ""

    def _input(self, item):
        """
        Find the input field (text input or textarea) within a chatbot item.
        Filters out hidden, submit, button, and file input types.
        
        Args:
            item: Chatbot item WebElement
            
        Returns:
            WebElement: Input field element, or None if not found
        """
        try:
            # Find regular text inputs (not hidden, submit, button, or file)
            fields = item.find_elements(
                By.XPATH,
                ".//input[not(@type='hidden') and not(@type='submit') "
                "and not(@type='button') and not(@type='file')]",
            )
            # Also include textarea elements
            fields += item.find_elements(By.XPATH, ".//textarea")

            for field in fields:
                try:
                    if field.is_displayed() and field.is_enabled():
                        return field
                except Exception:
                    pass
        except Exception:
            pass

        return None
