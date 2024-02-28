exports.main = async function (event, context) {
  console.log("Printing Headers: ", event.headers);

  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      caller: "Hi Invioso! It's Zuora Calling!",
      zuoraRequestHeader: event.headers,
    }),
  };
};
