from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.common.exceptions
import time


# # get google.co.in
# driver.get("https://google.com")
# # search_bar = driver.find_element(By.XPATH, "//textarea[@name='q']")
# search_bar = driver.find_element(By.NAME, "q")
# search_bar.clear()
# search_bar.send_keys("weather in nyc")
# search_bar.send_keys(Keys.RETURN)


def unsubscribe(unsubscribeURL):
    # create webdriver object
    driver = webdriver.Edge()

    """if it isn't a simple checkbox, we can just open the window for them"""
    driver.get(unsubscribeURL)
    try:
        checkbox = driver.find_element(By.ID, "_objUnsubAllChk")
        update_button = driver.find_element(By.CLASS_NAME, "buttontext")

        # if we already checked it before, we pass it
        if not checkbox.is_selected():
            checkbox.click()
            update_button.click()
        time.sleep(5)
        driver.close()
    # if checkbox isn't found, we leave the window open
    except selenium.common.exceptions.NoSuchElementException:
        print("No checkbox was found")
        try:
            while driver.current_window_handle in driver.window_handles:
                time.sleep(1)
        # if user closes the window, we move on
        except selenium.common.exceptions.NoSuchWindowException:
            pass
    return 0