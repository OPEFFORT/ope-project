from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import platform
import sys
import time

if len(sys.argv) <= 1:
    print("Invalid number of arguments")
    exit(1)

token = sys.argv[1]
url = "http://127.0.0.1:8888/lab?token=" + token
chrome_options = Options()

if platform.system() == 'Windows' or platform.system() == 'Darwin':
    chrome_options.add_experimental_option('detach', True)
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=chrome_options)
elif platform.system() == 'Linux':
    chrome_options.add_argument('--headless') # Inorder for Action to run, it needs to be headless
    driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install(), chrome_type=ChromeType.GOOGLE), options=chrome_options)
    #driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=chrome_options) #kes og command changed due to vers mismatof chrome
else:
    print("Unknown OS")
    exit(1)

print("Accessing url: "+url)
driver.get(url)

driver.implicitly_wait(45)

driver.save_screenshot('main_screenshot.png')
print("Saved main screenshot")


main_window_handle = driver.current_window_handle #used to return to base screen for next test


new_nb_button = driver.find_element(By.XPATH, '//div[@data-category="Notebook"]')
print("Found new notebook button")

new_nb_button.click()
time.sleep(10)

driver.save_screenshot('new_nb_screenshot.png')
print("Saved new notebook screenshot")


rise_button = driver.find_element(By.XPATH, '//button[@data-command="RISE:preview"]')
print("Found RISE presentation button")
rise_button.click()

time.sleep(10)
driver.save_screenshot('rise_screenshot.png')
print("Saved rise screenshot")


toolbar = driver.find_element(By.XPATH, "//div[@class='lm-Widget p-Widget jp-Toolbar' and @role='navigation']")
fullscreen_button = toolbar.find_element(By.XPATH,".//button[@title='Open the slideshow in full screen']")
fullscreen_button.click()
is_fullscreen = driver.execute_script("return document.fullscreenElement !== null")
print("fullscreen button is functioning")

print("Rise Extension is working!")

print("returning to homepage")

driver.switch_to.window(main_window_handle)
driver.refresh()


