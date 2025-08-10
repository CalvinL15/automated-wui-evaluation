#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup, Comment
import time
from commons.create_webdriver import create_webdriver


class DOMAnalyzer:
    def __init__(self, url='', html=None):
        self.driver = create_webdriver('DOMAnalyzer')
        self.url = url
        self.html = html

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def analyze_url(self):
        if not self.driver:
            raise ValueError("Driver is not initialized.")
        self.driver.get(self.url)
        time.sleep(1)  # Allow time for the page to load completely
        return self.analyze_html(self.driver.page_source)

    # check if an element is visible
    def visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def analyze_html(self, html_content=None):
        if not self.driver:
            raise ValueError("Driver is not initialized.")
        if html_content is None:
            if self.html:
                html_content = self.html
            else:
                raise ValueError("HTML content is not provided.")
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.find_all(True)
        visible_texts = filter(self.visible, soup.find_all(text=True))
        text_content = " ".join(t.strip() for t in visible_texts)
        element_data = []
        for element in elements:
            el_data = {
                'tag': element.name,
                'attributes': element.attrs,
                'children': [child.name for child in element.children if child.name is not None]
            }
            element_data.append(el_data)

        return {
            "text": text_content,
            "elements": element_data
        }
