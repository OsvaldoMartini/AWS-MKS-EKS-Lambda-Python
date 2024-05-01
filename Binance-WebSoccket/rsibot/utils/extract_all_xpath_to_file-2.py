import requests
from lxml import html

def save_html(url, filename):
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"HTML page saved as {filename}")
        else:
            print("Failed to download HTML page")
    except Exception as e:
        print("Failed to download HTML page:", e)

def extract_xpath(html_file):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            tree = html.fromstring(f.read())
            xpath_exprs = tree.xpath('//*')  # Get all elements
            return [tree.getroottree().getpath(element) for element in xpath_exprs]
    except Exception as e:
        print("Failed to extract XPath:", e)
        return []

def main():
    url = "https://www.fnz.com/contact"
    filename = "fnz_contact.html"
    xpath_filename = "xpath-python-found-2.txt"

    save_html(url, filename)
    xpaths = extract_xpath(filename)

    print("\nXPaths extracted from the HTML page:")
    for xpath in xpaths:
        print(xpath)

    # Save the extracted XPaths to a file
    with open(xpath_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xpaths))
    print(f"XPaths saved to {xpath_filename}")

if __name__ == "__main__":
    main()
