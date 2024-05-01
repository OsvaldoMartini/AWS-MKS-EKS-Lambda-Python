import requests
import re
from lxml import html

def save_html(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"HTML page saved as {filename}")
        else:
            print(f"Failed to download HTML page: {response.status_code} {response.reason}")
    except Exception as e:
        print("Failed to download HTML page:", e)

def extract_xpath(html_file):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            tree = html.fromstring(f.read())
            xpath_exprs = tree.xpath('//*')  # Get all elements
            xpaths = [get_xpath(element) for element in xpath_exprs]
            return xpaths
    except Exception as e:
        print("Failed to extract XPath:", e)
        return []

def get_xpath(element):
    xpath = []
    for e in element.iterancestors():
        xpath.insert(0, e.tag)
    return '/' + '/'.join(f"{tag}[{get_index(tag, element)}]" for tag in xpath)

def get_index(tag, element):
    count = 0
    for e in element.itersiblings(preceding=True):
        if e.tag == tag:
            count += 1
    return count + 1

def main():
    url = "https://www.fnz.com/contact"
    filename = "fnz_contact.html"
    xpath_filename = "xpath-python-found-4.txt"

    save_html(url, filename)
    xpaths = extract_xpath(filename)

    print("\nXPaths extracted from the HTML page:")
    for xpath in xpaths:
        print(xpath)

    with open(xpath_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xpaths))
    print(f"XPaths saved to {xpath_filename}")

if __name__ == "__main__":
    main()
