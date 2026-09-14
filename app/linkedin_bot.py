import os
import time
import logging
import base64  # Added: Required for decoding Base64 encoded session cookies
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "santoshchourasiya2011@gmail.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
PLAYWRIGHT_ENDPOINT = os.getenv("PLAYWRIGHT_ENDPOINT")

# Path to store session cookies for persistence and bypassing bot detection checks
COOKIE_FILE = "/tmp/linkedin_state.json"

# Added: Restore session cookies from Kubernetes Secret environment variable upon startup
encoded_cookies = os.getenv("LINKEDIN_COOKIES")
if encoded_cookies and not os.path.exists(COOKIE_FILE):
    with open(COOKIE_FILE, "wb") as f:
        f.write(base64.b64decode(encoded_cookies))
    logging.info("Restored LinkedIn session cookies from Kubernetes Secret.")

def apply_on_linkedin(job_title: str, resume_path: str):
    logging.info(f"Starting LinkedIn automation for: {job_title}")
    
    if not LINKEDIN_PASSWORD:
        logging.error("LINKEDIN_PASSWORD environment variable is missing. Skipping LinkedIn application.")
        return

    with sync_playwright() as p:
        # Added: Check if previous session cookies exist to reuse them
        context_args = {}
        if os.path.exists(COOKIE_FILE):
            context_args["storage_state"] = COOKIE_FILE
            logging.info("Found existing session cookies. Loading state to bypass login.")

        if PLAYWRIGHT_ENDPOINT:
            logging.info(f"Connecting to remote Playwright browser at {PLAYWRIGHT_ENDPOINT}")
            browser = p.chromium.connect(PLAYWRIGHT_ENDPOINT)
            context = browser.new_context(**context_args) # Added: Pass saved context state if available
        else:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-setuid-sandbox", "--disable-infobars"])
            context_args["user_agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            context = browser.new_context(**context_args) # Added: Pass saved context state if available

        page = context.new_page()

        try:
            # Modified: Try loading feed directly first to utilize saved session cookies
            logging.info("Navigating to LinkedIn feed...")
            page.goto("https://www.linkedin.com/feed/", timeout=60000)

            # Added: If redirected to login/auth page, cookies are invalid/missing, fallback to credentials
            if "login" in page.url or "uas" in page.url or "checkpoint" in page.url:
                logging.info("Session expired or missing. Navigating to login page...")
                page.goto("https://www.linkedin.com/login", timeout=60000)
                
                try:
                    page.fill("#username", LINKEDIN_EMAIL, timeout=10000)
                    page.fill("#password", LINKEDIN_PASSWORD)
                    page.click("button[type='submit']")
                except Exception:
                    logging.warning("Automated login blocked or selectors changed. Please complete login manually if browser is visible...")
                    page.wait_for_url("**/feed/**", timeout=60000)
            
            # Wait for successful feed load or security redirect
            page.wait_for_url("**/feed/**", timeout=20000)
            logging.info("Successfully logged into LinkedIn.")

            # Added: Save current session state/cookies for future CronJob runs
            context.storage_state(path=COOKIE_FILE)
            logging.info("LinkedIn session cookies saved successfully.")

            # \033[91m# Added: Directly use global search bar from LinkedIn Feed instead of navigating to Jobs home page\033[0m
            time.sleep(3)
            logging.info(f"Searching for role directly from feed: {job_title}")
            
            global_search = page.locator("input.search-global-typeahead__input").first
            if global_search.is_visible(timeout=10000):
                global_search.click()
                global_search.fill(job_title)
                page.keyboard.press("Enter")
                time.sleep(5)
            else:
                # Fallback: navigate via direct search query URL since global search bar selector can change
                search_url = f"https://www.linkedin.com/search/results/jobs/?keywords={job_title.replace(' ', '%20')}"
                page.goto(search_url, timeout=45000, wait_until="domcontentloaded")
                time.sleep(5)

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