from selenium import webdriver
from bs4 import BeautifulSoup

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # You can use any other WebDriver based on your browser choice
driver.get("https://www.fnz.com/contact")  # URL of the page you want to scrape

# Get the page source after letting the JavaScript execute
html = driver.page_source

# Close the WebDriver
driver.quit()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# Dictionary to store unique dropdown (select) elements
unique_select_elements = {}

# Find all unique dropdown (select) elements
for select in soup.find_all("select"):
    # Determine the name of the select element
    name = select.get("name") or select.get("id")
    # Add the select element to the dictionary
    unique_select_elements[name] = select

# Dictionary to store dropdown options
dropdown_options = {}

# Extract options for each unique dropdown element
for name, select_element in unique_select_elements.items():
    options = select_element.find_all("option")
    options_text = [option.text.strip() for option in options]
    dropdown_options[name] = options_text

# Print dropdown options
print("Dropdown options:")
for dropdown_name, options in dropdown_options.items():
    print(f"{dropdown_name} options: {options}")
