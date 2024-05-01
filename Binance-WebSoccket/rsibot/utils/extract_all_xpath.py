import requests
from lxml import html

def save_html(url, filename):
    response = requests.get(url, verify=False)  # Disable SSL certificate verification
    if response.status_code == 200:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"HTML page saved as {filename}")
    else:
        print("Failed to download HTML page")

def extract_xpath(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        tree = html.fromstring(f.read())
        xpath_exprs = tree.xpath('//*')  # Get all elements
        return [tree.getroottree().getpath(element) for element in xpath_exprs]

if __name__ == "__main__":
    url = "https://www.fnz.com/contact"
    filename = "fnz_contact.html"

    save_html(url, filename)
    xpaths = extract_xpath(filename)

    print("\nXPaths extracted from the HTML page:")
    for xpath in xpaths:
        print(xpath)
