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

# Find all unique HTML elements
unique_elements = set()
for tag in soup.find_all():
    unique_elements.add(tag.name)

# Print the unique HTML elements
print("Unique HTML elements found on the page:")
for element in unique_elements:
    print(element)
