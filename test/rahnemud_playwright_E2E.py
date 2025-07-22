import json

from playwright.sync_api import sync_playwright

from config import *
from utils.balebot_utils import send_message_to_bale
from utils.playwright_utils import click_accept_cookie
from utils.utils import update_test_status, send_sms


def test_login_rahnemud():
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
            current_step = "باز کردن صفحه لاگین"
            page.goto(RAHNEMUD_URL, timeout=60000)
            click_accept_cookie(page)

            current_step = "وارد کردن نام کاربری"
            page.fill('input[id=":r0:"]', RAHNEMUD_USERNAME)

            current_step = "وارد کردن رمز عبور"
            page.fill('input[id=":r1:"]',  RAHNEMUD_PASSWORD)

            current_step = "کلیک روی دکمه ورود"
            page.click('button#login-btn')

            current_step = "صبر برای لود شدن صفحه اصلی"
            page.wait_for_load_state("networkidle")

            current_step = "بررسی موفقیت لاگین"
            if page.locator("p", has_text="پروفایل ادمین").first.is_visible():
                message += "✅ لاگین با موفقیت انجام شد\n"
            else:
                message += f"❌ لاگین انجام شد ولی المان مورد انتظار دیده نشد\n"
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

def test_login_rahnemud2():
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
            current_step = "باز کردن صفحه لاگین"
            page.goto(RAHNEMUD_URL2, timeout=60000)
            click_accept_cookie(page)

            current_step = "وارد کردن نام کاربری"
            page.fill('input[id=":r0:"]', RAHNEMUD_USERNAME2)

            current_step = "وارد کردن رمز عبور"
            page.fill('input[id=":r1:"]',  RAHNEMUD_PASSWORD2)

            current_step = "کلیک روی دکمه ورود"
            page.click('button#login-btn')

            current_step = "صبر برای لود شدن صفحه اصلی"
            page.wait_for_load_state("networkidle")

            current_step = "بررسی موفقیت لاگین"
            if page.locator("p", has_text="پروفایل ادمین").first.is_visible():
                message += "✅ لاگین با موفقیت انجام شد\n"
            else:
                message += f"❌ لاگین انجام شد ولی المان مورد انتظار دیده نشد\n"
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

def rahnemud_test():
    message = "🖥️ سامانه رهنمود :\n\n"

    status_message = test_login_rahnemud()
    m = status_message["message"]
    update_test_status("test_login_rahnemud" , status_message["status_err"] , RAHNEMUD_STATUS_FILE)
    message += f"🔐 تست لاگین به سامانه 7111 :\n{m}\n\n"

    status_message = test_login_rahnemud2()
    m = status_message["message"]
    update_test_status("test_login_rahnemud2" , status_message["status_err"] , RAHNEMUD_STATUS_FILE)
    message += f"🔐 تست لاگین به سامانه 7109 :\n{m}\n\n"


    print(message)
    M = check_status_messages_and_notify()
    print(M)


    send_message_to_bale(message)

def check_status_messages_and_notify():
    with open(RAHNEMUD_STATUS_FILE, "r") as file:
        status = json.load(file)

    messages = []

    if status.get("test_login_rahnamud", 0) > 3:
        messages.append("❌ ورود به سامانه رهنمود بیش از ۳ بار با خطا مواجه شده است.")

    total_message = "\n".join(messages)

    if total_message:
        send_sms(total_message, DrRahmaniMobile)
        send_sms(total_message, AllahGholiMobile)
        send_sms(total_message, NoursalehiMobile)

    return total_message