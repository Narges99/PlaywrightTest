from playwright.sync_api import sync_playwright
from config import DADKAV_URL , contradiction_detection_url
from utils.playwright_utils import check_status
from utils.elasticsearch_utils import log_to_elasticsearch
from utils.balebot_utils import send_message_to_bale

def test_check_status():
    result = check_status(DADKAV_URL)
    message = ""
    if result["success"]:
        message = f"✅ سامانه دادکاو در دسترس است\n⏱ زمان پاسخ: {result['response_time']} ثانیه"
        _report("بالا بودن سامانه دادکاو",message, DADKAV_URL , True , "سامانه دادکاو" )
    else:
        message = f"❌ سامانه در دسترس نیست\n⚠️ خطا: {result['error'] or 'کد وضعیت: ' + str(result['status_code'])}"
        _report("بالا بودن سامانه دادکاو", message, DADKAV_URL, False, "سامانه دادکاو")


def test_contradiction_detection():
    current_step = "شروع تست"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            current_step = "صفحه اولیه تناقض‌یابی"
            page.goto(contradiction_detection_url, timeout=50000)

            current_step = "وارد کردن متن"
            page.fill("textarea", "این یک تست تناقض‌یابی است")
            click_next_step(page)

            current_step = "غنی‌سازی"
            click_next_step(page)

            current_step = "شباهت‌سنجی"
            click_next_step(page)

            current_step = "تناقض‌یابی"
            click_next_step(page)

            current_step = "بررسی وجود پیام خطا"
            if page.locator("text=خطا").first.is_visible():
                _report("تناقض‌یابی",f"❌ خطا در {current_step}ظاهر شد", contradiction_detection_url, False, current_step)
            else:
                _report("تناقض‌یابی","✅ تناقض‌یابی با موفقیت انجام شد", contradiction_detection_url, True, current_step)

        except Exception as e:
            _report("تناقض‌یابی",f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}", contradiction_detection_url, False, current_step)
        finally:
            browser.close()

def click_next_step(page):
    button = page.locator('button:has-text("مرحله بعد")').filter(has=page.locator(":visible")).last
    button.scroll_into_view_if_needed()
    page.evaluate("""() => {
        const blocker = document.querySelector('.styles_fixed_box__PO7al');
        if (blocker) blocker.style.display = 'none';
    }""")
    button.click(force=True)

def _report(scenario , message, url, success: bool, step: str):
    print(message)
    send_message_to_bale(message)
    # log_to_elasticsearch({
    #     "scenario": scenario,
    #     "url": url,
    #     "success": success,
    #     "message": message,
    #     "failed_step": None if success else step
    # })