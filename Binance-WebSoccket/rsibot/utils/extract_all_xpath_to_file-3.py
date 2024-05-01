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
            xpaths_with_index = []
            for element in xpath_exprs:
                xpath = get_xpath_with_index(element)
                xpaths_with_index.append(xpath)
            return xpaths_with_index
    except Exception as e:
        print("Failed to extract XPath:", e)
        return []

def get_xpath_with_index(element):
    xpath = []
    for e in element.iterancestors():
        xpath.insert(0, e.tag)
    return '/'.join([f"{tag}[{idx}]" for idx, tag in enumerate(xpath, start=1)])

def main():
    url = "https://www.fnz.com/contact"
    filename = "fnz_contact.html"
    xpath_filename = "xpath-python-found-3.txt"

    save_html(url, filename)
    xpaths_with_index = extract_xpath(filename)

    print("\nXPaths extracted from the HTML page with corresponding indices:")
    for xpath in xpaths_with_index:
        print(xpath)

    # Save the extracted XPaths with index to a file
    with open(xpath_filename, 'w', encoding='utf-8') as f:
        for xpath in xpaths_with_index:
            f.write(f"{xpath}\n")
    print(f"XPaths with corresponding indices saved to {xpath_filename}")

if __name__ == "__main__":
    main()
