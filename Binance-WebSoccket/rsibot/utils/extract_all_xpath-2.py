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

def search_elements(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        tree = html.fromstring(f.read())
        elements_to_search = ['INPUT', 'BUTTON', 'MAT_SELECT', 'MAT_OPTION', 'MAT_EXPANSION_PANEL', 'ANCHOR', 'SELECT', 'OPTION', 'summary']
        total_found = {}
        for element in elements_to_search:
            xpath_expr = f"//{element}"
            elements_found = tree.xpath(xpath_expr)
            total_found[element] = len(elements_found)
        return total_found

if __name__ == "__main__":
    url = "https://www.fnz.com/contact"
    filename = "fnz_contact.html"

    save_html(url, filename)
    elements_count = search_elements(filename)

    print("\nTotal occurrences of elements:")
    for element, count in elements_count.items():
        print(f"{element}: {count}")
