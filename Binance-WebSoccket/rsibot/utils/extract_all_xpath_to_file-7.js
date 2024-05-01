const { Builder, By } = require("selenium-webdriver");
const chrome = require("selenium-webdriver/chrome");
const fs = require("fs");

async function extractFullXPath(url) {
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

    // Find all elements on the page
    const elements = await driver.findElements(By.xpath("//*"));

    // Generate full XPath for each element
    for (const element of elements) {
      const fullXPath = await getFullXPath(driver, element);
      xpathExpressions.push(fullXPath);
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

async function getFullXPath(driver, element) {
  return await driver.executeScript(
    `
    function getFullXPath(element) {
      const segments = [];
      for (; element && element.nodeType == Node.ELEMENT_NODE; element = element.parentNode) {
        let segment = element.nodeName.toLowerCase();
        if (element.id) {
          segment += "[@id='" + element.id + "']";
          segments.unshift(segment);
          break;
        } else {
          let siblingCount = 0;
          let siblingIndex = 0;
          for (let sibling = element.previousSibling; sibling; sibling = sibling.previousSibling) {
            if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE) {
              continue;
            }
            if (sibling.nodeName == element.nodeName) {
              ++siblingCount;
            }
          }
          for (let sibling = element.nextSibling; sibling; sibling = sibling.nextSibling) {
            if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE) {
              continue;
            }
            if (sibling.nodeName == element.nodeName) {
              ++siblingCount;
            }
          }
          if (siblingCount > 1) {
            siblingIndex = siblingCount;
            segment += '[' + siblingIndex + ']';
          }
          segments.unshift(segment);
        }
      }
      return segments.length ? '/' + segments.join('/') : '';
    }
    return getFullXPath(arguments[0]);
  `,
    element
  );
}

async function main() {
  const url = "https://www.fnz.com/contact";
  const xpathFilename = "xpath-javascript-found-7.txt";

  const xpaths = await extractFullXPath(url);

  console.log("\nFull XPaths extracted from the web page:");
  xpaths.forEach((xpath) => console.log(xpath));

  // Save the extracted XPaths to a file
  fs.writeFileSync(xpathFilename, xpaths.join("\n"), "utf-8");
  console.log(`XPaths saved to ${xpathFilename}`);
}

main();
