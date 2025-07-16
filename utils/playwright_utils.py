import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

def check_status(url: str):

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-gpu",
                "--disable-software-rasterizer"
            ]
        )
        page = browser.new_page()
        start = time.time()

        try:
            response = page.goto(url, timeout=60000, wait_until="domcontentloaded")
            if response.status != 200:
                raise Exception(f"HTTP Status Code: {response.status}")

            try:
                page.wait_for_load_state("networkidle", timeout=30000)
                page.wait_for_selector('button:has-text("جستجو")', timeout=15000)
            except PlaywrightTimeoutError:
                return {
                    "success": True,
                    "status_code": 200,
                    "response_time": round(time.time() - start, 2),
                    "error": "Timeout waiting for full load, but HTTP status was OK"
                }

            elapsed = round(time.time() - start, 2)
            return {
                "success": True,
                "status_code": 200,
                "response_time": elapsed,
                "error": None
            }

        except Exception as e:
            elapsed = round(time.time() - start, 2)
            return {
                "success": False,
                "status_code": None,
                "response_time": elapsed,
                "error": str(e)
            }
        finally:
            browser.close()

def click_accept_cookie(page):
    try:
        accept_button = page.locator('button:has-text("پذیرش")')
        if accept_button.is_visible():
            accept_button.click()

    except Exception as e:
        message =  f"❌ خطا در کلیک روی دکمه 'پذیرش': {e}"