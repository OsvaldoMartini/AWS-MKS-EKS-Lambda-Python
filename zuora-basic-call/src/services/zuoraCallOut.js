exports.main = async function (event, context) {
  console.log(event);
  console.log("AWS_REGION: ", process.env.AWS_REGION);
  return {
    statusCode: 200,
    body: JSON.stringify("Hi Invioso! It's Zuora Calling!"),
  };
};
