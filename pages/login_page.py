# ============================================================================
# LOGIN PAGE - NAUKRI AUTHENTICATION
# ============================================================================
# Handles Naukri.com login process including:
# - Opening the Naukri homepage
# - Finding and clicking login button
# - Entering credentials (email and password)
# - Handling OTP/CAPTCHA verification when required

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage, log

# Default fallback credentials (should be overridden by environment variables)
USERNAME = "ashishparte9298@gmail.com"
PASSWORD = "Parte@1234"


class LoginPage(BasePage):
    """Handles Naukri.com login and authentication."""
    
    def open(self):
        """
        Open Naukri homepage and close any popup dialogs.
        Waits for page load before proceeding.
        """
        self.driver.get("https://www.naukri.com/")
        time.sleep(7)
        self.close_common_popups()

    def login(self, username, password):
        """
        Complete login process with provided credentials.
        Handles OTP/CAPTCHA verification if required.
        
        Args:
            username: Naukri account email
            password: Naukri account password
            
        Raises:
            ValueError: If credentials are empty
            RuntimeError: If username or password field not found
        """
        username = username or USERNAME
        password = password or PASSWORD

        # Validate credentials are provided
        if not username:
            raise ValueError(
                "NAUKRI_USERNAME is empty. Set it in your environment before running."
            )

        if not password:
            raise ValueError(
                "NAUKRI_PASSWORD is empty. Set it in your environment before running."
            )

        self.open()
        self._open_login_dialog()

        # Find and fill username field (multiple selectors for different page versions)
        username_box = self.find_visible_element(
            [
                (By.XPATH, "//input[@type='email']"),
                (
                    By.XPATH,
                    "//input[contains(translate(@placeholder,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'email')]",
                ),
                (
                    By.XPATH,
                    "//input[contains(translate(@placeholder,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'username')]",
                ),
            ],
            15,
        )

        if username_box is None:
            raise RuntimeError("Naukri username field not found.")

        username_box.clear()
        username_box.send_keys(username)

        # Find and fill password field
        password_box = self.find_visible_element(
            [(By.XPATH, "//input[@type='password']")], 10
        )

        if password_box is None:
            raise RuntimeError("Naukri password field not found.")

        password_box.clear()
        password_box.send_keys(password)

        # Find and click login button (try multiple selectors)
        submit_button = self.find_visible_element(
            [
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'login')]",
                ),
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'sign in')]",
                ),
                (By.XPATH, "//input[@type='submit']"),
            ],
            10,
        )

        if submit_button:
            self.click_element(submit_button)
        else:
            # Fallback: press Enter key
            password_box.send_keys(Keys.ENTER)

        time.sleep(7)
        
        # Check if OTP or CAPTCHA verification is required
        body_text = self.visible_body_text()
        if "otp" in body_text or "captcha" in body_text:
            log("OTP / CAPTCHA detected. Complete verification in browser.")
            time.sleep(30)  # Wait for manual verification

    def _open_login_dialog(self):
        """
        Find and click the 'Login' button to open the login dialog.
        Handles different button implementations (links vs buttons).
        """
        login_button = self.find_visible_element(
            [
                (
                    By.XPATH,
                    "//a[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'login')]",
                ),
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'login')]",
                ),
            ],
            10,
        )

        if login_button:
            self.click_element(login_button)
            time.sleep(4)
