require("dotenv").config({ path: "./.env" });
var W3CWebSocket = require("websocket").w3cwebsocket;
const ccxt = require("ccxt");
require("axios-debug-log");
const axios = require("axios");

const MARKET_TYPE = "spot";
// const MARKET_TYPE = "margin";
//  const  MARKET_TYPE = "future";

const ASSET = "BTC";
const BASE = "USDT";

const tick = async (config, binanceClient) => {
  const { asset, base, spred, allocation } = config;
  const market = `${asset}/${base}`;
  const symbolToRate = market.replace("/", "");

  const orders = await binanceClient.fetchOpenOrders(market);
  orders.forEach(async (order) => {
    try {
      await binanceClient.cancelOrder(order.id, order.info.symbol);
      // user was successfully created
      console.log(`
      Order Closed ${order.id} Symbol: ${order.info.symbol}
    `);

      // business logic goes here
    } catch (error) {
      console.error(error); // from creation
    }
  });

  const result = await Promise.all([
    axios.get(
      // "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
      // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
      //"https://fapi.binance.com/fapi/v1/ticker/price?symbol=SEIUSDT"
      // "https://fapi.binance.com/fapi/v1/ticker/price?symbol=1000BONKUSDT"
      `https://api.binance.com/api/v3/ticker/price?symbol=${symbolToRate}`
    ),
    // axios.get(
    //   "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
    //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
    // ),

    // axios.get(
    //   "https://fapi.binance.com/fapi/v2/positionRisk?symbol=1000BONKUSDT"
    //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
    // ),
    // axios.get(
    //   "https://fapi.binance.com/fapi/v2/positionRisk?symbol=XMRUSDT"
    //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
    // ),
    // axios.get(
    //   "https://fapi.binance.com/fapi/v2/positionRisk?symbol=BEAMXUSDT"
    //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
    // ),
    // axios.get(
    //   "https://fapi.binance.com/fapi/v2/positionRisk?symbol=STXUSDT"
    //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
    // ),

    // https://fapi.binance.com/fapi/v2/positionRisk?symbol=1000BONKUSDT&timestamp=1702853580832&signature=ca7f9f94abc876aa4fed4cf7b35c311ce935d2abfcbbbbf48293806d1a1313ec
  ]);

  // result[1] = "0.999809";
  console.log("Positions:", result[1]);
  result[1] = "1";

  // Give us the Price in the Unit we want
  //const marketPrice = result[0].data.bitcoin.usd / result[1].data.tether.usd;
  const marketPrice = result[0].data.price / result[1];
  // Calulcating the Parameters for the new order
  // const sellPrice = marketPrice * (1 + spred);
  // const buyPrice = marketPrice * (1 - spred);
  const sellPrice = marketPrice + (marketPrice * spred) / 100;
  const buyPrice = marketPrice - (marketPrice * spred) / 100;

  // Return all the Balance for all Cryptocurrencies
  const balances = await binanceClient.fetchBalance();
  // Extract the Bitcoin
  const assetBalance = balances.free[asset]; // Initial balance of Bitcoin or USDT
  // Extract Tether
  const baseBalance = balances.free[base]; // Initial balance of Tether
  //Calculates the Sell Volume
  const sellVolume = assetBalance / allocation;

  //Calculates the Buy Volume
  const buyVolume = (baseBalance * allocation) / marketPrice;

  console.log(`
  	New tick for ${market}
  	Created limit sell order for ${sellVolume}@${sellPrice}
  	Created limit buy order for ${sellVolume}@${buyPrice}
  `);

  // Sending the Order to Binance
  // await binanceClient.createLimitSellOrder(
  //   market,
  //   sellVolume.toFixed(0),
  //   sellPrice.toFixed(3)
  // );
  // await binanceClient.createLimitBuyOrder(
  //   market,
  //   buyVolume.toFixed(0),
  //   buyPrice.toFixed(3)
  // );

  try {
    await binanceClient.createLimitSellOrder(
      market,
      sellVolume.toFixed(3),
      sellPrice.toFixed(1)
    );
    // user was successfully created
    console.log(`
      New tick for SELL ${market}
      Created limit sell order for ${sellVolume}@${sellPrice}
    `);

    // business logic goes here
  } catch (error) {
    console.log(`
      New tick for SELL ${market}
      Created limit sell order for ${sellVolume}@${sellPrice}
    `);
    console.error(error); // from creation
  }

  // sideEffectType: "AUTO_BORROW_REPAY",
  // type: "LIMIT",
  // placeType: "order-form",
  // positionSide: "BOTH",
  // reduceOnly:false,

  try {
    await binanceClient.createLimitBuyOrder(
      market,
      buyVolume.toFixed(3),
      buyPrice.toFixed(1)
    );
    // user was successfully created
    console.log(`
    New tick for BUY ${market}
    Created limit buy order for ${sellVolume}@${buyPrice}
    `);
    // business logic goes here
  } catch (error) {
    console.log(`
    New tick for BUY ${market}
    Created limit buy order for ${sellVolume}@${buyPrice}
    `);
    console.error(error); // from creation
  }
};

const run = () => {
  const config = {
    // asset: "1000BONK",
    // asset: "SEI",
    asset: ASSET,
    base: BASE,
    allocation: 4.199, //Percentage of our  portfolio to allocate for each trade
    spred: 0.5, //Spread Percentage mid rate Buy or Sell limit order example:  10.000 our sale limit will be 12.000 and buy order will be 8.000
    tickInterval: 2000, // every 2 seconds evaluate  goig to sell or buy the limit order of the preious ticket  and create new one
  };

  const binanceClient = new ccxt.binance({
    apiKey: process.env.API_KEY,
    secret: process.env.API_SECRET,
    verbose: true,
    headers: {
      "X-MBX-APIKEY": process.env.API_KEY,
    },
    options: {
      defaultType: MARKET_TYPE,
    },
  });

  tick(config, binanceClient);
  setInterval(tick, config.tickInterval, config, binanceClient);
};

// https://api.binance.com/api/v3/openOrders?symbol=BNBUSDT&recvWindow=4000&timestamp={{timestamp}}&signature=95c0a9af68533202da19f7509a08fa8a557da078f87af9d033d0aee017aff79e
run();
