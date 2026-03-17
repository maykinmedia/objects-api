import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from playwright.sync_api import sync_playwright


class PlaywrightSyncLiveServerTestCase(StaticLiveServerTestCase):
    playwright = None
    browser = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    @classmethod
    def live_reverse(cls, viewname, args=None, kwargs=None):
        path = reverse(viewname, args=args, kwargs=kwargs)
        return f"{cls.live_server_url}{path}"

    def get_user_login_state(self, user):
        context = self.browser.new_context()
        page = context.new_page()

        page.goto(self.live_reverse("admin:login"))
        page.get_by_label("Username").fill(user.username)
        page.get_by_label("Password").fill("secret")
        page.get_by_role("button", name="Log in").click()

        try:
            page.wait_for_selector("#site-name", timeout=5000)
        except Exception:
            print(f"Login failed. Current URL: {page.url}")
            raise

        state = context.storage_state()
        context.close()
        return state
