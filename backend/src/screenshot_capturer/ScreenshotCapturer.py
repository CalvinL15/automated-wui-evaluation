#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import time

from commons.create_webdriver import create_webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from PIL import Image


class ScreenshotCapturer:
    def __init__(self):
        self.driver = create_webdriver('ScreenshotCapturer')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def capture_screenshot_url(self, url):
        if not self.driver:
            raise ValueError("Driver is not initialized.")

        if not url:
            raise ValueError("No URL provided.")

        self.driver.get(url)
        try:
            # Wait for the document.readyState to be complete
            WebDriverWait(self.driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # wait 5 seconds for dynamic page content to load
            time.sleep(5)
        except TimeoutException:
            # If the complete state is not reached within 5 seconds, this block is executed
            print("Timed out waiting for page to load completely. Proceeding with the actions.")

        screenshot_as_png = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot_as_png)).convert("RGB")
        return image

    def capture_screenshot_html(self, html_path):
        if not self.driver:
            raise ValueError("Driver is not initialized.")
        if not html_path:
            raise ValueError("No HTML path provided.")
        self.driver.get(f'file://{html_path}')
        # Wait for the page to fully load
        self.driver.implicitly_wait(5)
        screenshot_as_png = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot_as_png)).convert("RGB")
        return image

