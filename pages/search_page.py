# ============================================================================
# SEARCH PAGE - JOB LISTING SEARCH AND EXTRACTION
# ============================================================================
# Handles job search functionality:
# - Building search URLs with keywords and locations
# - Executing searches on Naukri
# - Scrolling through job listings to load more jobs
# - Extracting job details (title, company, location, URL)
# - Pagination through search results

import re
import time

from selenium.webdriver.common.by import By

from Naukari.config import JOB_KEYWORD, MAX_SCROLLS
from Naukari.pages.base_page import BasePage, log


class SearchPage(BasePage):
    """Handles job search and extraction from Naukri search results."""
    
    # Multiple CSS/XPath selectors for job card containers (different page layouts)
    CARD_SELECTORS = [
        "//div[contains(@class,'srp-jobtuple-wrapper')]",
        "//div[contains(@class,'cust-job-tuple')]",
        "//article[contains(@class,'jobTuple')]",
        "//article",
        "//div[contains(@class,'jobTuple')]",
    ]

    def __init__(self, driver):
        """
        Initialize SearchPage with driver and set to track URLs in current run.
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.current_run_urls = set()  # Track extracted URLs to avoid duplicates

    def build_search_url(self, location):
        """
        Build Naukri search URL from job keyword and location.
        Converts text to URL-friendly slugs.
        
        Args:
            location: Job location string (e.g., "Mumbai")
            
        Returns:
            str: Complete Naukri search URL
        """
        keyword_slug = self._slug(JOB_KEYWORD)
        location_slug = self._slug(location)
        return f"https://www.naukri.com/{keyword_slug}-jobs-in-{location_slug}"

    def search(self, location):
        """
        Execute job search for a specific location.
        
        Args:
            location: Job location to search in
            
        Returns:
            bool: True if jobs found, False otherwise
        """
        search_url = self.build_search_url(location)
        log(f"SEARCHING: {JOB_KEYWORD}")
        log(f"LOCATION: {location}")
        log(f"Search URL: {search_url}")

        self.driver.get(search_url)
        time.sleep(8)
        self.close_common_popups()
        return len(self._job_cards()) > 0

    def scroll_page(self):
        """
        Scroll down the page to load more job listings.
        Stops when page height doesn't increase (no more jobs to load).
        Scrolls up to MAX_SCROLLS times.
        """
        last_height = 0

        for count in range(MAX_SCROLLS):
            # Scroll to bottom of page
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            log(f"Scroll {count + 1}")

            # Stop scrolling if page height hasn't increased (no more jobs)
            if new_height == last_height:
                break

            last_height = new_height

    def extract_jobs(self, location):
        """
        Extract job information from visible job cards on the page.
        
        Args:
            location: Current search location (used as fallback for job location)
            
        Returns:
            list: List of job dictionaries with title, company, location, URL, status
        """
        jobs = []
        cards = self._job_cards()
        log(f"Job cards found: {len(cards)}")

        for card in cards:
            try:
                title_element = self._title_element(card)

                if title_element is None:
                    continue

                title = title_element.text.strip()
                url = (title_element.get_attribute("href") or "").strip()

                # Skip if title/URL empty or URL already extracted in this run
                if not title or not url or url in self.current_run_urls:
                    continue

                self.current_run_urls.add(url)
                jobs.append(
                    {
                        "title": title,
                        "company": self._company(card),
                        "location": self._job_location(card, location),
                        "url": url,
                        "status": "Not Processed",
                        "date": "",
                    }
                )
            except Exception as error:
                log("Extraction error:", error)

        return jobs

    def go_to_next_page(self):
        """
        Find and click the 'Next' button to go to next search results page.
        
        Returns:
            bool: True if next button found and clicked, False otherwise
        """
        next_button = self.find_visible_element(
            [
                (
                    By.XPATH,
                    "//a[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'next')]",
                ),
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'next')]",
                ),
                (By.XPATH, "//a[contains(@class,'next')]"),
            ],
            5,
        )

        if next_button is None:
            return False

        try:
            self.click_element(next_button)
            time.sleep(6)
            return True
        except Exception:
            return False

    def _job_cards(self):
        """
        Find all visible job card elements on the page.
        Tries multiple CSS/XPath selectors until one returns results.
        
        Returns:
            list: List of WebElement job cards
        """
        for selector in self.CARD_SELECTORS:
            try:
                cards = self.driver.find_elements(By.XPATH, selector)
                visible_cards = [card for card in cards if card.is_displayed()]

                if visible_cards:
                    return visible_cards
            except Exception:
                continue

        return []

    def _title_element(self, card):
        """
        Find the job title link element within a job card.
        Tries multiple CSS/XPath selectors.
        
        Args:
            card: Job card WebElement
            
        Returns:
            WebElement: Job title link element, or None if not found
        """
        selectors = [
            ".//a[contains(@class,'title')]",
            ".//a[contains(@class,'jobTitle')]",
            ".//a[contains(@class,'job-title')]",
            ".//h2//a",
            ".//h3//a",
        ]

        for selector in selectors:
            try:
                element = card.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return element
            except Exception:
                continue

        return None

    def _company(self, card):
        """
        Extract company name from job card.
        
        Args:
            card: Job card WebElement
            
        Returns:
            str: Company name or "Not Found" if not found
        """
        selectors = [
            ".//a[contains(@class,'comp-name')]",
            ".//a[contains(@class,'company')]",
            ".//*[contains(@class,'companyName')]",
        ]
        return self._first_visible_text(card, selectors, "Not Found")

    def _job_location(self, card, default_location):
        """
        Extract job location from job card.
        Uses provided default_location if location not found in card.
        
        Args:
            card: Job card WebElement
            default_location: Location to use as fallback
            
        Returns:
            str: Job location or default_location
        """
        selectors = [
            ".//*[contains(@class,'loc')]",
            ".//*[contains(@class,'location')]",
            ".//*[contains(@class,'jobLocation')]",
        ]
        return self._first_visible_text(card, selectors, default_location)

    def _first_visible_text(self, card, selectors, default):
        """
        Find first visible element matching selectors and return its text.
        
        Args:
            card: Parent WebElement to search within
            selectors: List of XPath selectors to try
            default: Default value if no element found
            
        Returns:
            str: Element text or default value
        """
        for selector in selectors:
            try:
                element = card.find_element(By.XPATH, selector)
                if element.is_displayed():
                    value = element.text.strip()
                    if value:
                        return value
            except Exception:
                continue

        return default

    def _slug(self, value):
        """
        Convert text to URL-friendly slug (lowercase, replace non-alphanumeric).
        Example: "Test Automation" -> "test-automation"
        
        Args:
            value: Text to convert
            
        Returns:
            str: URL-friendly slug
        """
        return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")
