const fs = require("fs");
const { JSDOM } = require("jsdom");

async function saveHTML(url, filename) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(
        `Failed to download HTML page: ${response.status} ${response.statusText}`
      );
    }
    const htmlContent = await response.text();
    fs.writeFileSync(filename, htmlContent, "utf-8");
    console.log(`HTML page saved as ${filename}`);
  } catch (error) {
    console.error("Failed to download HTML page:", error);
  }
}

function extractXPath(htmlFile) {
  try {
    const htmlContent = fs.readFileSync(htmlFile, "utf-8");
    const { window } = new JSDOM(htmlContent);
    const document = window.document;
    const elements = document.querySelectorAll("*");
    const xpaths = Array.from(elements).map((element) => getXPath(element));
    return xpaths;
  } catch (error) {
    console.error("Failed to extract XPath:", error);
    return [];
  }
}

function getXPath(element) {
  const idx = (sib, name) =>
    sib
      ? idx(sib.previousElementSibling, name || sib.localName) +
        (sib.localName == name)
      : 1;
  const segs = [];
  for (; element && element.nodeType == 1; element = element.parentNode)
    segs.unshift(element.localName.toLowerCase() + "[" + idx(element) + "]");
  return segs.length ? "/" + segs.join("/") : null;
}

async function main() {
  const url = "https://www.fnz.com/contact";
  const filename = "fnz_contact.html";
  const xpathFilename = "xpath-javascript-found-4.txt";

  await saveHTML(url, filename);
  const xpaths = extractXPath(filename);

  console.log("\nXPaths extracted from the HTML page:");
  xpaths.forEach((xpath) => console.log(xpath));

  // Save the extracted XPaths to a file
  fs.writeFileSync(xpathFilename, xpaths.join("\n"), "utf-8");
  console.log(`XPaths saved to ${xpathFilename}`);
}

main();
