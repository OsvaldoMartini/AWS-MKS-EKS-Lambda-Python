const fs = require("fs");
const { JSDOM } = require("jsdom");

function saveHTML(url, filename) {
  try {
    const htmlContent = fs.readFileSync(filename, "utf-8");
    console.log(`HTML content read from ${filename}`);
    return htmlContent;
  } catch (error) {
    console.error("Failed to read HTML file:", error);
    return null;
  }
}

function extractXPath(htmlContent) {
  try {
    const { window } = new JSDOM(htmlContent);
    const document = window.document;
    const elements = document.querySelectorAll("*");
    const xpathsWithIndex = Array.from(elements).map((element) =>
      getXPathWithIndex(element)
    );
    return xpathsWithIndex;
  } catch (error) {
    console.error("Failed to extract XPath:", error);
    return [];
  }
}

function getXPathWithIndex(element) {
  let xpath = [];
  for (let e = element; e; e = e.parentElement) {
    xpath.unshift(e.tagName.toLowerCase());
  }
  return "/" + xpath.map((tag, idx) => `${tag}[${idx + 1}]`).join("/");
}

function main() {
  const filename = "fnz_contact.html";
  const xpathFilename = "xpath-javascript-found-3.txt";

  const htmlContent = saveHTML(null, filename);
  if (!htmlContent) {
    console.log("HTML content not available.");
    return;
  }

  const xpathsWithIndex = extractXPath(htmlContent);

  console.log(
    "\nXPaths extracted from the HTML page with corresponding indices:"
  );
  xpathsWithIndex.forEach((xpath) => console.log(xpath));

  // Save the extracted XPaths with index to a file
  fs.writeFileSync(xpathFilename, xpathsWithIndex.join("\n"), "utf-8");
  console.log(`XPaths with corresponding indices saved to ${xpathFilename}`);
}

main();
