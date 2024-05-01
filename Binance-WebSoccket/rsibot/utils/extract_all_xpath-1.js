const fs = require("fs");
const axios = require("axios");
const { JSDOM } = require("jsdom");

async function saveHTML(url, filename) {
  try {
    const response = await axios.get(url);
    fs.writeFileSync(filename, response.data, "utf-8");
    console.log(`HTML page saved as ${filename}`);
  } catch (error) {
    console.error("Failed to download HTML page:", error);
  }
}

function extractXPath(htmlFile) {
  const htmlContent = fs.readFileSync(htmlFile, "utf-8");
  const { window } = new JSDOM(htmlContent);
  const document = window.document;
  const elements = document.querySelectorAll("*");
  const xpaths = Array.from(elements).map((element) => getXPath(element));
  return xpaths;
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
  const xpathFilename = "xpath-javascript-found-2.txt";

  await saveHTML(url, filename);
  const xpaths = extractXPath(filename);

  console.log("\nXPaths extracted from the HTML page:");
  xpaths.forEach((xpath) => console.log(xpath));

  // Save XPaths to a file
  fs.writeFileSync(xpathFilename, xpaths.join("\n"), "utf-8");
  console.log(`XPaths saved to ${xpathFilename}`);
}

main();
