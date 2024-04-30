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

# Find all span elements
span_elements = soup.find_all("span")

# Print the text content inside each span element
print("Text inside span elements:")
for span in span_elements:
    text_inside_span = span.get_text(strip=True)
    if text_inside_span:
        print(text_inside_span)
