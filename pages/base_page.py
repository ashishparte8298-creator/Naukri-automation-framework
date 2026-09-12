# ============================================================================
# BASE PAGE - COMMON SELENIUM UTILITIES
# ============================================================================
# Base class providing common Selenium utility methods used by all page objects.
# Handles element finding with retries, popup closing, and safe element clicking.

import sys
import time

from selenium.webdriver.common.by import By


def log(message):
    """Print message with immediate flush to ensure real-time output."""
    print(message, flush=True)
    sys.stdout.flush()


class BasePage:
    """Base page class with common Selenium operations for all pages."""
    
    def __init__(self, driver):
        """
        Initialize with Selenium WebDriver.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver

    def find_visible_element(self, selectors, timeout=20):
        """
        Find and return the first visible element from a list of selectors.
        Retries until timeout is reached. Useful when element visibility varies.
        
        Args:
            selectors: List of (By, locator) tuples to try in order
            timeout: Maximum seconds to wait for element visibility (default: 20)
            
        Returns:
            WebElement: First visible element found, or None if not found
        """
        end_time = time.time() + timeout

        while time.time() < end_time:
            for locator in selectors:
                try:
                    elements = self.driver.find_elements(*locator)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                return element
                        except Exception:
                            pass
                except Exception:
                    pass

            time.sleep(0.5)

        return None

    def close_common_popups(self):
        """
        Attempt to close common popup dialogs using multiple close button selectors.
        Handles different popup implementations (Close buttons, X buttons, close divs).
        """
        selectors = [
            "//button[contains(@aria-label,'Close')]",
            "//button[contains(@aria-label,'close')]",
            "//button[normalize-space()='x']",
            "//button[normalize-space()='×']",
            "//span[contains(@class,'close')]",
            "//div[contains(@class,'close')]",
        ]

        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    try:
                        if element.is_displayed():
                            self.driver.execute_script(
                                "arguments[0].click();", element
                            )
                            time.sleep(0.3)
                    except Exception:
                        pass
            except Exception:
                pass

    def visible_body_text(self):
        """
        Get all visible text on the page body in lowercase.
        Useful for checking page state with keywords like 'applied', 'error', etc.
        
        Returns:
            str: Lowercase text content of page body, or empty string if error
        """
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text.lower()
        except Exception:
            return ""

    def click_element(self, element):
        """
        Safely click an element by scrolling it into view first.
        Uses JavaScript click if regular click fails.
        
        Args:
            element: WebElement to click
        """
        # Scroll element to center of viewport
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", element
        )
        time.sleep(0.5)

        try:
            element.click()
        except Exception:
            # Fallback to JavaScript click if normal click fails
            self.driver.execute_script("arguments[0].click();", element)
