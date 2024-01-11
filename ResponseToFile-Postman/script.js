const express = require("express");
const { format } = require("path");
app = express();
fs = require("fs");
shell = require("shelljs");
const fns = require("date-fns");

// Modify the folder path in which responses need to be stored
folderPath = "./Responses/";
defaultFileExtension = "json"; // Change the default file extension
bodyParser = require("body-parser");
DEFAULT_MODE = "writeFileSync";
path = require("path");

// Create the folder path in case it doesn't exist
shell.mkdir("-p", folderPath);

// Change the limits according to your response size
app.use(bodyParser.json({ limit: "50mb", extended: true }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: true }));

app.get("/", (req, res) =>
  res.send("Hello, I write data to file. Send them requests!")
);

app.post("/write", (req, res) => {
  // console.log(req.body);
  let extension = req.body.fileExtension || defaultFileExtension,
    fsMode = req.body.mode || DEFAULT_MODE,
    uniqueIdentifier = req.body.uniqueIdentifier
      ? typeof req.body.uniqueIdentifier === "boolean"
        ? Date.now()
        : req.body.uniqueIdentifier
      : req.query["symbol"] + "-" + fns.format(Date.now(), "yyyyMMdd-hh-mm-ss");

  // filename = `${req.body.requestName}${uniqueIdentifier || ""}`;
  filename = `${uniqueIdentifier || ""}`;
  filePath = `${path.join(folderPath, filename)}.${extension}`;
  options = req.body.options || undefined;

  let data = req.body;
  // fs.writeFileSync(filePath, JSON.stringify(data));

  fs[fsMode](filePath, JSON.stringify(data, null, 4), options, (err) => {
    if (err) {
      console.log(err);
      res.send("Error");
    } else {
      res.send("Success");
    }
  });
});

app.listen(3000, () => {
  console.log(
    "ResponsesToFile App is listening now! Send them requests my way!"
  );
  console.log(
    `Data is being stored at location: ${path.join(process.cwd(), folderPath)}`
  );
});
