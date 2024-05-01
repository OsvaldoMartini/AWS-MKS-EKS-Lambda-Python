const { Builder, By } = require("selenium-webdriver");
const chrome = require("selenium-webdriver/chrome");
const fs = require("fs");

async function extractXPath(url) {
  // Set up Chrome options
  const options = new chrome.Options();
  options.addArguments("--headless"); // Run Chrome in headless mode
  options.addArguments("--disable-gpu"); // Disable GPU acceleration (to prevent graphical glitches)

  // Create a new Chrome session
  const driver = await new Builder()
    .forBrowser("chrome")
    .setChromeOptions(options)
    .build();

  try {
    // Navigate to the URL
    await driver.get(url);

    const xpathExpressions = [];

    // Replace this with your specific XPath expressions
    const xpaths = [
      "//div[@class='example']",
      "//a[contains(@href, 'example.com')]",
      "//input[@type='text']",
    ];

    for (const xpath of xpaths) {
      const elements = await driver.findElements(By.xpath(xpath));

      for (const element of elements) {
        const absoluteXPath = await getAbsoluteXPath(driver, element);
        xpathExpressions.push(absoluteXPath);
      }
    }

    return xpathExpressions;
  } catch (error) {
    console.error("Failed to extract XPath:", error);
    return [];
  } finally {
    // Close the browser session
    await driver.quit();
  }
}

async function getAbsoluteXPath(driver, element) {
  // Execute JavaScript in the browser to get the absolute XPath of the element
  return await driver.executeScript(
    `
    function getAbsoluteXPath(element) {
      const parts = [];
      for (; element && element.nodeType == Node.ELEMENT_NODE; element = element.parentNode) {
        let index = 0;
        for (let sibling = element.previousSibling; sibling; sibling = sibling.previousSibling) {
          if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE) {
            continue;
          }
          if (sibling.nodeName == element.nodeName) {
            ++index;
          }
        }
        const tagName = element.nodeName.toLowerCase();
        const id = element.id ? "[@id='" + element.id + "']" : '';
        const className = element.className ? "[@class='" + element.className + "']" : '';
        parts.unshift(tagName + id + className + '[' + (index + 1) + ']');
      }
      return parts.length ? '/' + parts.join('/') : '';
    }
    return getAbsoluteXPath(arguments[0]);
  `,
    element
  );
}

async function main() {
  const url = "https://www.fnz.com/contact";

  const xpaths = await extractXPath(url);

  console.log("\nXPaths extracted from the web page:");
  xpaths.forEach((xpath) => console.log(xpath));
}

main();
