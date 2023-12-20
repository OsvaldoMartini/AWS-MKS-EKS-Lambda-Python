var W3CWebSocket = require("websocket").w3cwebsocket;
// var WebSocket = require("ws");

// Spot
var binanceSocket = new W3CWebSocket(
  // "wss://stream.binance.com:9443/ws/ethusdt@kline_1s"
  "wss://stream.binance.com:9443/ws/bonkusdt@kline_1s"
);

binanceSocket.onerror = function () {
  console.log("Connection Error");
};

// binanceSocket.onopen = function () {
//   console.log("WebSocket Client Connected");

//   function sendNumber() {
//     if (binanceSocket.readyState === binanceSocket.OPEN) {
//       var number = Math.round(Math.random() * 0xffffff);
//       binanceSocket.send(number.toString());
//       setTimeout(sendNumber, 1000);
//     }
//   }
//   sendNumber();
// };

// binanceSocket.onclose = function () {
//   console.log("echo-protocol Client Closed");
// };

// binanceSocket.onmessage = function (e) {
//   if (typeof e.data === "string") {
//     console.log("Received: '" + e.data + "'");
//   }
// };

// bnbbtc
// wss://stream.binance.com:9443/ws/bnbbtc@depth
// btcusdt
// wss://stream.binance.com:9443/ws/btcusdt@depth

binanceSocket.onmessage = function (event) {
  var message = JSON.parse(event.data);

  var candlestick = message.k;

  console.log("Real time: ", candlestick);
};
