const zuoraCredentials = {
  client_id: "f50b1c58-c026-49e5-860c-13dc699a6940",
  client_secret: "+d2Z+MJc5hEXSqBH9kn=/28TBE8FWGzxtT91ht",
  // username: "your_username",
  // password: "your_password",
};

// Construct request body
const requestData = {
  grant_type: "client_credentials", //"password" , "client_credentials",  "authorization_code"
  client_id: zuoraCredentials.client_id,
  client_secret: zuoraCredentials.client_secret,
  // username: zuoraCredentials.username,
  // password: zuoraCredentials.password,
};

// Define Sandbox Zuora token endpoint
const sandbox_us_rest_api = "https://rest.test.zuora.com/oauth/token";

// Encode data for URL
const encodedData = Object.keys(requestData)
  .map(
    (key) =>
      encodeURIComponent(key) + "=" + encodeURIComponent(requestData[key])
  )
  .join("&");

// Make HTTP POST request to Zuora token endpoint
fetch(sandbox_us_rest_api, {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: encodedData,
})
  .then((response) => {
    if (!response.ok) {
      throw new Error("Failed to obtain Zuora token");
    }
    return response.json();
  })
  .then((data) => {
    console.log("Zuora Access Token:", data.access_token);
    console.log("Zuora Token Type:", data.token_type);
    console.log("Expires In:", data.expires_in, "seconds");
    return;
  })
  .catch((error) => {
    console.error("Error:", error);
  });
