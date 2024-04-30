from selenium import webdriver
from w3c_validator import HTMLValidator

# Launch Selenium WebDriver
driver = webdriver.Chrome()

# Navigate to your web page
driver.get("https://www.fnz.com/contact")

# Get the page source
html_source = driver.page_source

# Validate HTML using w3c_validator
validator = HTMLValidator()
results = validator.validate_text(html_source)

# Print the results
for message in results.messages:
    print(message)

# Close the WebDriver
driver.quit()
