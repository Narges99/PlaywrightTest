from playwright.sync_api import sync_playwright
import json

from config import *
from utils.balebot_utils import send_message_to_bale
from utils.utils import update_test_status, send_sms


def test_crowdsourcing_login():
    current_step = "شروع تست"
    message = ""
    status_err = False

    with sync_playwright() as p:
        browser = p.firefox.launch(
            headless=False,
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
            current_step = "باز کردن صفحه لاگین"
            page.goto(CROWDSOURCING_URL, timeout=60000)

            current_step = "وارد کردن شماره موبایل"
            page.fill('input[id=":r0:"]', CROWDSOURCING_MOBILE)

            current_step = "کلیک روی دکمه ورود"
            page.click('button#login-btn')

            current_step = "صبر برای ظاهر شدن فیلد کد تایید"
            page.wait_for_selector('input[id=":r1:"]', timeout=15000)

            current_step = "وارد کردن کد تایید"
            page.fill('input[id=":r1:"]', CROWDSOURCING_CONFIRM)

            current_step = "کلیک روی دکمه تایید کد"
            page.click('button#confirm-code')

            current_step = "صبر برای نمایش 'کارتابل من'"
            page.wait_for_selector("p:has-text('کارتابل من')", timeout=10000)

            current_step = "بررسی ظاهر شدن 'کارتابل من'"
            page.wait_for_load_state("networkidle")

            if page.locator("p", has_text="کارتابل من").first.is_visible():
                message += "✅ لاگین دو مرحله‌ای با موفقیت انجام شد (کارتابل من دیده شد)\n"
            else:
                message += "❌ لاگین انجام شد ولی 'کارتابل من' دیده نشد\n"
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


def crowdsourcing_test():
    message = "🖥️ سامانه سجعه:\n\n"

    status_message = test_crowdsourcing_login()
    m = status_message["message"]
    update_test_status("test_crowdsourcing_login" , status_message["status_err"] , DADKAV_STATUS_FILE)
    message += f"🔐 تست لاگین به سامانه:\n{m}\n\n"


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
            if test_name == "test_crowdsourcing_login":
                messages.append("❌ ورود به سامانه سجعه بیش از ۳ بار با خطا مواجه شده است.")
    total_message = "\n".join(messages)

    if total_message:
        send_sms(total_message, DrRahmaniMobile)
        send_sms(total_message, AllahGholiMobile)
        send_sms(total_message, NoursalehiMobile)

    return "\n".join(messages)