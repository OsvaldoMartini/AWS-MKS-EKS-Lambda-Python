exports.main = async function (event, context) {
  console.log(event);

  return {
    statusCode: 200,
    body: JSON.stringify("Hi Invioso! It's Zuora Calling!"),
  };
};
