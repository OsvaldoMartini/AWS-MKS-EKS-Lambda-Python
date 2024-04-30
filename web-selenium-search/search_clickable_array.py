from selenium import webdriver
from bs4 import BeautifulSoup
# import requests

# Replace the URL below with the URL of the webpage you want to scrape
url ="https://www.fnz.com/contact"

# Fetch the HTML content of the page
# response = requests.get(url)
# html_content = response.content

# Launch Selenium WebDriver (assuming Chrome)
driver = webdriver.Chrome()

# Navigate to your web page
driver.get("https://www.fnz.com/contact")

# Get the page source
html_source = driver.page_source

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_source, 'html.parser')

# Define a list of element types to search for
element_types = ["input", "button", "form", "textarea", "mat-expansion-panel", "a", "mat-select", "mat-option", "select", "option"]

# Find clickable elements of the specified types
clickable_elements = []
for element_type in element_types:
    # elements = soup.find_all(element_type)
    elements = soup.find_all(lambda tag: tag.has_attr(element_type) or tag.has_attr('onclick'))
    print(elements)

    # for element in elements:
    #     # Check if the element is clickable (add further conditions as needed)
    #     if element.has_attr(element_type) or element.has_attr("onclick"):
    #         clickable_elements.append(element)

# Print the clickable elements
for element in clickable_elements:
    print(element)
