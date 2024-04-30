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

# Find all dropdown (select) elements
dropdown_elements = soup.find_all("select")
# unique_select_elements = soup.find_all("select", id=True, recursive=False)

# Dictionary to store dropdown options
dropdown_options = {}

# Iterate through each dropdown element
for index, dropdown in enumerate(dropdown_elements, start=1):
    # Find all option elements within the dropdown
    options = dropdown.find_all("option")
    # Extract and store the text of each option
    options_text = [option.text.strip() for option in options]
    # Store options in dictionary with index as key
    dropdown_options[f"Dropdown_{index}"] = options_text

# Print dropdown options
print("Dropdown options:")
for dropdown_name, options in dropdown_options.items():
    print(f"{dropdown_name} options: {options}")
