from selenium import webdriver

# Initialize the WebDriver for Chrome
driver = webdriver.Chrome()

# Navigate to a webpage
driver.get("https://www.fnz.com/contact")

# Perform actions, such as clicking links, filling forms, etc.
# For example, find an element by its CSS selector and click it
element = driver.find_element_by_css_selector("a[href='https://www.fnz.com/contact']")
element.click()

# After performing actions, you can perform further operations or close the browser
# driver.close()  # Close the current tab
# driver.quit()   # Close the entire browser window

