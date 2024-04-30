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
select_elements = []
for select in soup.find_all("select"):
    unique_select_elements.add(select["name"] if select.get("name") else select["id"])
    # Find all parents of the <select> tag
    parents = select.find_parents()
    
    # Build the XPath
    xpath_parts = [f"{parent.name}[{parent.attrs}]" for parent in parents]
    xpath_parts.reverse()
    xpath = "/".join(xpath_parts)
    
    select_elements.append((select, xpath))

# Print the unique dropdown (select) elements
print("Dropdown (select) elements found on the page:")
for element, xpath in select_elements:
    print(f"Element XPath: {xpath}")
