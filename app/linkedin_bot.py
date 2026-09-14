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

# Marker strings that show up in the URL when LinkedIn serves a security
# checkpoint / verification / auth-wall page instead of the real page you asked for.
CHALLENGE_MARKERS = ["checkpoint", "uas", "authwall", "login", "add-phone", "captcha"]


def is_challenge_url(url: str) -> bool:
    return any(marker in url for marker in CHALLENGE_MARKERS)


def dump_debug_state(page, tag: str):
    """Best-effort screenshot + URL/title dump so a hung/blocked navigation
    can actually be diagnosed instead of just showing a bare timeout."""
    try:
        logging.warning(f"[debug:{tag}] current URL: {page.url}")
        logging.warning(f"[debug:{tag}] current title: {page.title()}")
        path = f"/tmp/linkedin_debug_{tag}.png"
        page.screenshot(path=path, full_page=True)
        logging.warning(f"[debug:{tag}] screenshot saved to {path}")
    except Exception as dbg_err:
        logging.warning(f"[debug:{tag}] could not capture debug state: {dbg_err}")

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

        connected_remotely = bool(PLAYWRIGHT_ENDPOINT)
        if connected_remotely:
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

            # --- HUMAN-LIKE NAVIGATION INSTEAD OF DIRECT SEARCH URL ---
            logging.info("Navigating through UI to jobs section...")

            # Click on the Jobs icon/tab on LinkedIn feed if it's there, or navigate safely.
            # NOTE: is_visible() does NOT auto-wait, so give the nav bar a real chance to
            # hydrate before deciding it isn't there.
            navigated_via_nav_click = False
            try:
                jobs_nav = page.locator("a[href*='/jobs/']").first
                jobs_nav.wait_for(state="visible", timeout=8000)
                jobs_nav.click()
                navigated_via_nav_click = True
                time.sleep(3)
            except Exception:
                logging.info("Jobs nav link not found/clickable in time, falling back to direct URL.")

            if not navigated_via_nav_click:
                try:
                    # domcontentloaded instead of the default "load" — LinkedIn's SPA pages
                    # keep background requests running and the "load" event may never fire,
                    # which is what was causing the 60s timeouts.
                    page.goto("https://www.linkedin.com/jobs/", wait_until="domcontentloaded", timeout=45000)
                except Exception as goto_err:
                    dump_debug_state(page, "jobs_goto_failed")
                    raise goto_err

            # If LinkedIn served a checkpoint/verification/auth-wall page instead of Jobs,
            # bot-detection was triggered — stop cleanly instead of hanging on selectors
            # that will never appear.
            if is_challenge_url(page.url):
                dump_debug_state(page, "jobs_challenge")
                logging.error(
                    f"LinkedIn served a challenge/checkpoint page instead of Jobs (url={page.url}). "
                    "This is bot-detection, not a selector bug — see the debug screenshot."
                )
                return

            # Give the jobs page's own content a real target to wait for, rather than a
            # fixed sleep + the generic "load" event.
            try:
                page.wait_for_selector(
                    "input.jobs-search-box__text-input, input[aria-label*='Search'], .jobs-search-results-list",
                    timeout=20000,
                )
            except Exception:
                dump_debug_state(page, "jobs_page_not_ready")
                logging.warning("Jobs page loaded but expected search elements never appeared.")

            # Type keywords into the job search box naturally
            search_keyword = job_title.replace("_", " ")
            logging.info(f"Typing search keyword: {search_keyword}")
            
            # Wait for search input field and type slowly like a human
            search_input = page.locator("input.jobs-search-box__text-input, input[aria-label*='Search']").first
            search_input.click()
            time.sleep(1)
            search_input.fill(search_keyword)
            time.sleep(2)
            page.keyboard.press("Enter")
            
            # Allow results to load
            time.sleep(8)
            # ---------------------------------------------------------

            # Ensure page is stable before locating elements using multiple fallback selectors
            try:
                page.wait_for_selector(".jobs-search-results-list, .scaffold-layout__list, main", timeout=30000)
            except Exception as sel_err:
                logging.warning("Standard search list selector not found, checking page content...")
                # Safe screenshot capture wrapped in try-except to avoid crash if context closes
                try:
                    page.screenshot(path="/tmp/linkedin_debug.png", full_page=True)
                    logging.info("Saved debug screenshot to /tmp/linkedin_debug.png")
                except Exception as ss_err:
                    logging.warning(f"Could not take debug screenshot because browser closed: {ss_err}")
                raise sel_err

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
            # When connected via chromium.connect() (our shared playwright-service pod),
            # calling browser.close() tears down that whole remote browser instance —
            # closing just the context is enough and keeps the shared server healthy
            # for the next cronjob run.
            try:
                context.close()
            except Exception:
                pass
            if not connected_remotely:
                browser.close()
            logging.info("LinkedIn automation session closed.")