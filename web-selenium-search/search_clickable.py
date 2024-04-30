from selenium import webdriver
from bs4 import BeautifulSoup

# Launch Selenium WebDriver (assuming Chrome)
driver = webdriver.Chrome()

# Navigate to your web page
driver.get("https://www.fnz.com/contact")

# Get the page source
html_source = driver.page_source

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_source, 'html.parser')

# Find all clickable elements
clickable_elements = soup.find_all(lambda tag: tag.has_attr('href') or tag.has_attr('onclick'))

# Print clickable elements
for element in clickable_elements:
    print(element)
    # You can extract further information about the clickable elements if needed

# Close the WebDriver
driver.quit()
