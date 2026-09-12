# ============================================================================
# NAUKRI JOB APPLICATION - MAIN ENTRY POINT
# ============================================================================
# This is the main entry point for the Naukri job portal automation bot.
# It initializes a Selenium WebDriver, runs the job application flow, and
# ensures proper cleanup of browser resources.

import sys
from pathlib import Path

from selenium import webdriver

# Add project root to Python path to enable relative imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Naukari.naukri_flow import NaukriApplicationFlow, log


def create_driver():
    """
    Initialize and configure a Chrome WebDriver with appropriate options.
    
    Options:
    - start-maximized: Opens browser in full screen
    - disable-notifications: Prevents browser notifications from appearing
    - disable-popup-blocking: Allows popups (needed for Naukri dialogs)
    
    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    return webdriver.Chrome(options=options)


def main():
    """
    Main execution function:
    1. Creates a Chrome WebDriver
    2. Runs the Naukri job application automation flow
    3. Ensures browser is properly closed in all cases
    """
    driver = create_driver()

    try:
        # Initialize and run the automation flow
        flow = NaukriApplicationFlow(driver)
        flow.run()
    finally:
        # Always close browser, whether flow succeeds or fails
        log("Closing browser...")
        driver.quit()
        log("Browser closed.")


if __name__ == "__main__":
    main()
