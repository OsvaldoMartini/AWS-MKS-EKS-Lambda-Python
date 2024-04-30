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

# Find all unique dropdown (select) elements
unique_select_elements = set()
for select in soup.find_all("select"):
    unique_select_elements.add(select["name"] if select.get("name") else select["id"])

# Print the unique dropdown (select) elements
print("Unique dropdown (select) elements found on the page:")
for element in unique_select_elements:
    print(element)
