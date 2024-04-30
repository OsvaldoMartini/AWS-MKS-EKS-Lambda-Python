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

# Find all output and label elements
output_elements = soup.find_all("output")
label_elements = soup.find_all("label")

# Print the text content of output elements
print("Output elements:")
for output in output_elements:
    print(output.text.strip())

# Print the text content of label elements
# print("\nLabel elements:")
# for label in label_elements:
#     print(label.text.strip())
