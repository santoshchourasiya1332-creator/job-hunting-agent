import os
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.linkedin.com/login")
    
    input("Browser mein manually LinkedIn login complete karein, feed dikhne lage toh yahan terminal par Enter press karein...")
    
    context.storage_state(path="linkedin_state.json")
    print("Cookies successfully saved to linkedin_state.json!")
    browser.close()