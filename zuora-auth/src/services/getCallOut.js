exports.main = async function (event, context) {
  return {
    statusCode: 200,
    body: JSON.stringify(
      `Hello Invioso I am calling from Zuora Notifications! I will read from ${process.env.TABLE_NAME}`
    ),
  };
};
