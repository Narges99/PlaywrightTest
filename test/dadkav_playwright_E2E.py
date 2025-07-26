import json
import os
from playwright.sync_api import sync_playwright
from config import *
from utils.playwright_utils import check_status , click_accept_cookie
from utils.elasticsearch_utils import log_to_elasticsearch
from utils.balebot_utils import send_message_to_bale
from utils.utils import update_test_status, send_sms


def test_check_status():
    result = check_status(DADKAV_URL)
    message = ""
    status_err = False
    if result["success"]:
        message = f"✅ سامانه دادکاو در دسترس است\n⏱ زمان پاسخ: {result['response_time']} ثانیه"
    else:
        message = f"❌ سامانه در دسترس نیست\n⚠️ خطا: {result['error'] or 'کد وضعیت: ' + str(result['status_code'])}"
        status_err = True
    return {
            "status_err": status_err,
            "message": message
        }

def test_contradiction_detection():
    current_step = "شروع تست"
    message = ""
    status_err = False
    with sync_playwright() as p:
        browser = p.firefox.launch(
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
                status_err = True
            else:
                message += f"✅ تناقض‌یابی با موفقیت انجام شد\n"

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"
            status_err = True

        finally:
            browser.close()
    return  {
            "status_err": status_err,
            "message": message
        }

def test_search():
    message = ""
    status_err = False
    current_step = "شروع تست جستجو"

    with sync_playwright() as p:
        browser = p.firefox.launch(
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

        try:
            page.goto(DADKAV_URL, timeout=50000)

            current_step = "وارد کردن عبارت جستجو"
            search_input = page.locator('input[placeholder="عبارت مورد نظر خود را جستجو کنید ..."]')
            search_input.fill("تجارت الکترونیک")

            search_button = page.locator('button:has-text("جستجو")')
            search_button.click()
            current_step = "نتایج جستجو"
            page.wait_for_selector('tbody.MuiTableBody-root' , timeout=60000)

            if page.locator('tbody.MuiTableBody-root').count() > 0:
                message += "✅ جدول نتایج جستجو با موفقیت نمایش داده شد.\n"
            else:
                message += "❌ هیچ جدولی برای نتایج جستجو یافت نشد.\n"
                status_err = True

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"
            status_err = True

        finally:
            browser.close()

        response = {
            "status_err": status_err,
            "message": message
        }
    _report("تست جستجو - تجارت الکترونیک", message, DADKAV_URL, "✅" in message, current_step)
    return response

def test_summerize():
    message = ""
    status_err = False

    current_step = "شروع تست آپلود فایل و خلاصه‌سازی"

    with sync_playwright() as p:
        browser = p.firefox.launch(
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

        try:
            page.goto(SUMMERIZE_URL, timeout=50000)
            click_accept_cookie(page)

            current_step = "انتخاب فایل برای آپلود"

            base_dir = os.path.dirname(os.path.dirname(__file__))
            file_path = os.path.join(base_dir, 'utils', "summerize_text.txt")


            page.locator('label[for="file-upload"]').click()

            file_input = page.locator('#file-upload')
            file_input.set_input_files(file_path)

            page.wait_for_selector('p.MuiTypography-root:has-text("فایل‌های خود را اینجا بکشید")', timeout=6000)

            uploaded_file_name = page.locator('p.MuiTypography-root.muirtl-1k3b2k0').inner_text()
            if uploaded_file_name:
                message += "✅ فایل بارگذاری شد\n"
            else:
                message += "❌ فایل بارگذاری شده نمایش داده نشد.\n"
                status_err = True

            summarize_button = page.locator('button:has-text("خلاصه کن")')

            if summarize_button.is_disabled():
                message += "❌ دکمه 'خلاصه کن' غیرفعال است.\n"
                status_err = True
            else:
                summarize_button.click()
                current_step = "خلاصه سازی فایل بارگذاری شده"
                page.wait_for_selector('p.MuiTypography-root.muirtl-vr16bb', timeout=100000)

                if page.locator('p.MuiTypography-root.muirtl-vr16bb').is_visible():
                    message += "✅ خلاصه‌سازی با موفقیت انجام شد.\n"
                else:
                    message += "❌ مشکلی در خلاصه‌سازی به وجود آمد.\n"
                    status_err = True

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"
            status_err = True


        finally:
            browser.close()

    _report("تست آپلود فایل و خلاصه‌سازی", message, DADKAV_URL, "✅" in message, current_step)
    return  {
            "status_err": status_err,
            "message": message
        }

def test_smart_assistant():
    message = ""
    status_err = False
    current_step = "شروع تست سوال از سامانه"

    with sync_playwright() as p:
        browser = p.firefox.launch(
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
                status_err = True


        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}"
            status_err = True

        finally:
            browser.close()

    return {
            "status_err": status_err,
            "message": message
        }

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
    m = status_message["message"]
    update_test_status("test_check_status" , status_message["status_err"] , DADKAV_STATUS_FILE)
    message += f"🔍 تست وضعیت سامانه:\n{m}\n\n"

    search_message = test_search()
    m = search_message["message"]
    update_test_status("test_search" , search_message["status_err"] , DADKAV_STATUS_FILE)
    message += f"🔎 تست جستجو:\n{m}\n\n"

    contradiction_message = test_contradiction_detection()
    m = contradiction_message["message"]
    update_test_status("test_contradiction_detection" , contradiction_message["status_err"] , DADKAV_STATUS_FILE)
    message += f"⚖️ تست تناقض‌یابی:\n{m}\n\n"

    summerize_message = test_summerize()
    m = summerize_message["message"]
    update_test_status("test_summerize" , summerize_message["status_err"], DADKAV_STATUS_FILE)
    message += f"📝 تست خلاصه‌سازی:\n{m}\n\n"

    ask_question_message = test_smart_assistant()
    m = ask_question_message["message"]
    update_test_status("test_smart_assistant" , ask_question_message["status_err"], DADKAV_STATUS_FILE)
    message += f"❓ تست از من بپرس:\n{m}\n\n"

    print(message)
    M = check_status_messages_and_notify()
    print(M)


    send_message_to_bale(message)

def check_status_messages_and_notify():
    with open(DADKAV_STATUS_FILE, "r") as file:
        status = json.load(file)

    messages = []

    for test_name, count in status.items():
        if count > 3:
            if test_name == "test_check_status":
                messages.append("❌ سامانه دادکاو بیش از ۳ بار در دسترس نبوده است.")
            elif test_name == "test_search":
                messages.append("❌ بخش جستجو بیش از ۳ بار با مشکل مواجه شده است.")
            elif test_name == "test_contradiction_detection":
                messages.append("❌ بخش تناقض‌یابی بیش از ۳ بار با مشکل مواجه شده است.")
            elif test_name == "test_summerize":
                messages.append("❌ بخش خلاصه‌سازی بیش از ۳ بار با مشکل مواجه شده است.")
            elif test_name == "test_smart_assistant":
                messages.append("❌ بخش دستیار هوشمند بیش از ۳ بار با مشکل مواجه شده است.")
    if messages:
        total_message = "سامانه دادکاو:\n" + "\n".join(messages)
        send_sms(total_message, DrRahmaniMobile)
        send_sms(total_message, AllahGholiMobile)
        send_sms(total_message, NoursalehiMobile)

    return "\n".join(messages)

def _report(scenario, message, url, success: bool, step: str):
     print(message)
    # send_message_to_bale(message)
    # log_to_elasticsearch({
    #     "scenario": scenario,
    #     "url": url,
    #     "success": success,
    #     "message": message,
    #     "failed_step": None if success else step
    # })
