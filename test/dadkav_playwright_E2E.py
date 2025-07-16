import os
from playwright.sync_api import sync_playwright
from config import *
from utils.playwright_utils import check_status , click_accept_cookie
from utils.elasticsearch_utils import log_to_elasticsearch
from utils.balebot_utils import send_message_to_bale

def test_check_status():
    result = check_status(DADKAV_URL)
    message = ""
    if result["success"]:
        message = f"✅ سامانه دادکاو در دسترس است\n⏱ زمان پاسخ: {result['response_time']} ثانیه"
    else:
        message = f"❌ سامانه در دسترس نیست\n⚠️ خطا: {result['error'] or 'کد وضعیت: ' + str(result['status_code'])}"
    return message

def test_contradiction_detection():
    current_step = "شروع تست"
    message = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True ,   args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()

        try:
            current_step = "صفحه اولیه تناقض‌یابی"
            page.goto(CONTRADICTION_DETECTION_URL, timeout=50000)

            current_step = "وارد کردن متن"
            page.fill("textarea", LEGAL_FACT)
            click_next_step(page)

            current_step = "غنی‌سازی"
            click_next_step(page)

            current_step = "شباهت‌سنجی"
            click_next_step(page)

            current_step = "تناقض‌یابی"
            click_next_step(page)

            current_step = "بررسی وجود پیام خطا"
            if page.locator("text=خطا").first.is_visible():
                message += f"❌ خطا در {current_step} ظاهر شد\n"
            else:
                message += f"✅ تناقض‌یابی با موفقیت انجام شد\n"

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"

        finally:
            browser.close()

    return message

def test_search():
    message = ""
    current_step = "شروع تست جستجو"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True , args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()

        try:
            page.goto(DADKAV_URL, timeout=50000)

            current_step = "وارد کردن عبارت جستجو"
            search_input = page.locator('input[placeholder="عبارت مورد نظر خود را جستجو کنید ..."]')
            search_input.fill("تجارت الکترونیک")

            search_button = page.locator('button:has-text("جستجو")')
            search_button.click()

            page.wait_for_selector('tbody.MuiTableBody-root')

            if page.locator('tbody.MuiTableBody-root').count() > 0:
                message += "✅ جدول نتایج جستجو با موفقیت نمایش داده شد.\n"
            else:
                message += "❌ هیچ جدولی برای نتایج جستجو یافت نشد.\n"

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"

        finally:
            browser.close()

    _report("تست جستجو - تجارت الکترونیک", message, DADKAV_URL, "✅" in message, current_step)
    return message

def test_summerize():
    message = ""
    current_step = "شروع تست آپلود فایل و خلاصه‌سازی"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True , args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()

        try:
            page.goto(SUMMERIZE_URL, timeout=50000)
            click_accept_cookie(page)

            current_step = "انتخاب فایل برای آپلود"

            base_dir = os.path.dirname(os.path.dirname(__file__))
            file_path = os.path.join(base_dir, 'utils', "summerize_text.txt")


            page.locator('label[for="file-upload"]').click()

            file_input = page.locator('#file-upload')
            file_input.set_input_files(file_path)

            page.wait_for_selector('p.MuiTypography-root:has-text("فایل‌های خود را اینجا بکشید")', timeout=10000)

            uploaded_file_name = page.locator('p.MuiTypography-root.muirtl-1k3b2k0').inner_text()
            if uploaded_file_name:
                message += "✅ فایل بارگذاری شد\n"
            else:
                message += "❌ فایل بارگذاری شده نمایش داده نشد.\n"

            summarize_button = page.locator('button:has-text("خلاصه کن")')

            if summarize_button.is_disabled():
                message += "❌ دکمه 'خلاصه کن' غیرفعال است.\n"
            else:
                summarize_button.click()
                current_step = "خلاصه سازی فایل بارگذاری شده"
                page.wait_for_selector('p.MuiTypography-root.muirtl-vr16bb', timeout=50000)

                if page.locator('p.MuiTypography-root.muirtl-vr16bb').is_visible():
                    message += "✅ خلاصه‌سازی با موفقیت انجام شد.\n"
                else:
                    message += "❌ مشکلی در خلاصه‌سازی به وجود آمد.\n"

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"

        finally:
            browser.close()

    _report("تست آپلود فایل و خلاصه‌سازی", message, DADKAV_URL, "✅" in message, current_step)
    return message

def test_smart_assistant():
    message = ""
    current_step = "شروع تست سوال از سامانه"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True , args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()

        try:
            page.goto(SMART_ASSISTANT_URL, timeout=50000)
            click_accept_cookie(page)
            current_step = "وارد کردن سوال"

            question_text = "سن بازنشستگی در ایران چقدر است؟"
            page.locator('textarea[placeholder="هر سوالی دارید بپرسید ..."]').fill(question_text)

            send_button = page.locator('button:has-text("ارسال")')
            send_button.click()

            page.wait_for_selector('div[style="text-align: justify;"]', timeout=100000)

            if page.locator('div[style="text-align: justify;"]').is_visible():
                message += "✅ سوال با موفقیت ارسال شد و جواب دریافت شده است.\n"
            else:
                message += "❌ مشکل در ارسال سوال یا دریافت جواب.\n"

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"

        finally:
            browser.close()

    return message

def click_next_step(page):
    button = page.locator('button:has-text("مرحله بعد")').filter(has=page.locator(":visible")).last
    button.scroll_into_view_if_needed()
    page.evaluate("""() => {
        const blocker = document.querySelector('.styles_fixed_box__PO7al');
        if (blocker) blocker.style.display = 'none';
    }""")
    button.click(force=True)

def dadkav_test():
    message = "🖥️ سامانه دادکاو:\n\n"

    status_message = test_check_status()
    message += f"🔍 تست وضعیت سامانه:\n{status_message}\n\n"

    search_message = test_search()
    message += f"🔎 تست جستجو:\n{search_message}\n\n"

    contradiction_message = test_contradiction_detection()
    message += f"⚖️ تست تناقض‌یابی:\n{contradiction_message}\n\n"

    summerize_message = test_summerize()
    message += f"📝 تست خلاصه‌سازی:\n{summerize_message}\n\n"

    ask_question_message = test_smart_assistant()
    message += f"❓ تست از من بپرس:\n{ask_question_message}\n\n"


    send_message_to_bale(message)

def _report(scenario, message, url, success: bool, step: str):
     print(message)
     print(message)
    # send_message_to_bale(message)
    # log_to_elasticsearch({
    #     "scenario": scenario,
    #     "url": url,
    #     "success": success,
    #     "message": message,
    #     "failed_step": None if success else step
    # })
