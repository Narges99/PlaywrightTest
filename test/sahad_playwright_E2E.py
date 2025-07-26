import json

from playwright.sync_api import sync_playwright

from config import *
from utils.balebot_utils import send_message_to_bale
from utils.utils import update_test_status, send_sms


def test_login_with_captcha_check():
    current_step = "شروع تست"
    message = ""
    status_err = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            current_step = "باز کردن صفحه لاگین"
            page.goto(SAHAD_URL, timeout=60000)

            current_step = "وارد کردن شماره تلفن"
            page.fill('input[name="email"]', SAHAD_MOBILE)

            current_step = "وارد کردن کد امنیتی جعلی"
            page.fill('input[id=":r1:"]', SAHAD_CONFIRM)

            current_step = "کلیک روی دکمه ورود"
            page.click('button#login-btn')

            current_step = "بررسی پیام کپچا اشتباه"
            page.wait_for_load_state("networkidle", timeout=10000)
            page.wait_for_timeout(2000)

            if page.locator("p", has_text="لطفا کد امنیتی را به درستی وارد کنید").first.is_visible():
                message += "✅ فرم لاگین درست کار می‌کند (کپچا نادرست تشخیص داده شد)\n"
            else:
                message += "❌ هیچ پیام خطایی درباره کپچا نمایش داده نشد\n"
                status_err = True

        except Exception as e:
            message += f"❌ خطا در مرحله: {current_step}\n🟥 جزئیات: {e}\n"
            status_err = True

        finally:
            browser.close()

    return {
        "status_err": status_err,
        "message": message
    }

def sahad_test():
    message = "🖥️ سامانه سهاد:\n\n"

    status_message = test_login_with_captcha_check()
    m = status_message["message"]
    update_test_status("test_login_with_captcha_check" , status_message["status_err"] , SAHAD_STATUS_FILE)
    message += f"🔐 تست لاگین به سامانه:\n{m}\n\n"


    print(message)
    M = check_status_messages_and_notify()
    print(M)


    send_message_to_bale(message)


def check_status_messages_and_notify():
    with open(SAHAD_STATUS_FILE, "r") as file:
        status = json.load(file)

    messages = []

    for test_name, count in status.items():
        if count > 3:
            if test_name == "test_crowdsourcing_login":
                messages.append("❌تلاش برای ورود به سامانه  بیش از ۳ بار با خطا مواجه شده است.")
    if messages:
        total_message = "سامانه سهاد:\n" + "\n".join(messages)
        send_sms(total_message, DrRahmaniMobile)
        send_sms(total_message, AllahGholiMobile)
        send_sms(total_message, NoursalehiMobile)

    return "\n".join(messages)