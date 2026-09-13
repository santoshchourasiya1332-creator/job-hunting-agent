import os
import time
import logging
from playwright.sync_api import sync_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "santoshchourasiya2011@gmail.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
PLAYWRIGHT_ENDPOINT = os.getenv("PLAYWRIGHT_ENDPOINT")

def apply_on_linkedin(job_title: str, resume_path: str):
    logging.info(f"Starting LinkedIn automation for: {job_title}")
    
    if not LINKEDIN_PASSWORD:
        logging.error("LINKEDIN_PASSWORD environment variable is missing. Skipping LinkedIn application.")
        return

    with sync_api() as p:
        if PLAYWRIGHT_ENDPOINT:
            logging.info(f"Connecting to remote Playwright browser at {PLAYWRIGHT_ENDPOINT}")
            browser = p.chromium.connect(PLAYWRIGHT_ENDPOINT)
            context = browser.new_context()
        else:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

        page = context.new_page()

        try:
            logging.info("Navigating to LinkedIn login...")
            page.goto("https://www.linkedin.com/login", timeout=60000)
            page.fill("#username", LINKEDIN_EMAIL)
            page.fill("#password", LINKEDIN_PASSWORD)
            page.click("button[type='submit']")
            
            # Wait for successful feed load or security redirect
            page.wait_for_url("**/feed/**", timeout=20000)
            logging.info("Successfully logged into LinkedIn.")

            # Search target jobs with Easy Apply filter
            search_query = job_title.replace(" ", "%20")
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location=Pune%2C%20Maharashtra%2C%20India&f_LF=f_AL"
            
            logging.info(f"Navigating to job search URL: {search_url}")
            page.goto(search_url, timeout=30000)
            page.wait_for_selector(".jobs-search-results-list", timeout=15000)

            job_cards = page.locator(".job-card-container--clickable").all()
            logging.info(f"Found {len(job_cards)} job listings on page.")

            for i, card in enumerate(job_cards[:3]):  # Process top 3 listings
                try:
                    card.click()
                    time.sleep(2)

                    easy_apply_btn = page.locator("button.jobs-apply-button")
                    if easy_apply_btn.is_visible():
                        logging.info(f"Applying to job card {i+1} via Easy Apply...")
                        easy_apply_btn.click()
                        time.sleep(2)

                        # Handle modal fields / upload resume
                        file_input = page.locator("input[type='file']")
                        if file_input.is_visible():
                            file_input.set_input_files(resume_path)
                            logging.info(f"Uploaded tailored resume: {resume_path}")
                            time.sleep(2)

                        # Click through steps or submit
                        submit_btn = page.locator("button[aria-label='Submit application']")
                        if submit_btn.is_visible():
                            submit_btn.click()
                            logging.info("Application submitted successfully!")
                            time.sleep(3)
                        else:
                            # Close or dismiss if multi-step requires complex manual input
                            dismiss_btn = page.locator("button[aria-label='Dismiss']")
                            if dismiss_btn.is_visible():
                                dismiss_btn.click()
                                time.sleep(1)
                                discard_btn = page.locator("button[data-control-name='discard_application_confirm_btn']")
                                if discard_btn.is_visible():
                                    discard_btn.click()
                            logging.info("Skipped multi-step complex application form.")
                    else:
                        logging.info(f"Job card {i+1} is not an Easy Apply job. Skipping.")
                except Exception as card_err:
                    logging.warning(f"Error processing job card {i+1}: {card_err}")

        except Exception as e:
            logging.error(f"Error during LinkedIn automation workflow: {e}")
        finally:
            browser.close()
            logging.info("LinkedIn automation session closed.")