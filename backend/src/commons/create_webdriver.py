from selenium import webdriver
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()


def create_webdriver(component_name: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if component_name == 'ScreenshotCapturer':
        # Set specific options for ScreenshotCapturer
        options.add_argument("--window-size=1200,1200")
        options.add_argument('--start-maximized')
        options.add_argument('--start-fullscreen')

    # set your own executable_path, should be the path where chrome is located.
    return webdriver.Chrome(options=options)
