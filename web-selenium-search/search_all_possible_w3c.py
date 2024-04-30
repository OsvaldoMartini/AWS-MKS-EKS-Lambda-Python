from selenium import webdriver
from bs4 import BeautifulSoup

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # You can use any other WebDriver based on your browser choice
driver.get("https://www.fnz.com/contact")  # Replace with the URL of the page you want to scrape

# Get the page source after letting the JavaScript execute
html = driver.page_source

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# List of all W3C HTML elements
all_html_elements = [
    "a", "abbr", "address", "area", "article", "aside", "audio",
    "b", "base", "bdi", "bdo", "blockquote", "body", "br", "button",
    "canvas", "caption", "cite", "code", "col", "colgroup",
    "data", "datalist", "dd", "del", "details", "dfn", "dialog", "div", "dl", "dt",
    "em", "embed",
    "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hr", "html",
    "i", "iframe", "img", "input", "ins",
    "kbd", "keygen",
    "label", "legend", "li", "link",
    "main", "map", "mark", "menu", "menuitem", "meta", "meter",
    "nav", "noscript",
    "object", "ol", "optgroup", "option", "output",
    "p", "param", "picture", "pre", "progress",
    "q",
    "rb", "rp", "rt", "rtc", "ruby",
    "s", "samp", "script", "section", "select", "slot", "small", "source", "span", "strong", "style", "sub", "summary", "sup",
    "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track",
    "u", "ul",
    "var", "video",
    "wbr"
]

# Dictionary to store counts of elements by type
element_counts = {}

# Search for each element type using BeautifulSoup
for element in all_html_elements:
    elements = soup.find_all(element)
    count = len(elements)
    if count > 0:
        element_counts[element] = count

# Print total number of elements found for each type
for element, count in element_counts.items():
    print(f"Total number of <{element}> elements found: {count}")

# Close the WebDriver
driver.quit()
