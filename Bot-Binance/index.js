require("dotenv").config({ path: "./.env" });
const crypto = require("crypto");
// var W3CWebSocket = require("websocket").w3cwebsocket;
const ccxt = require("ccxt");
const queryString = require("querystring");
require("axios-debug-log");
const axios = require("axios");

// const MARKET_TYPE = "spot";
// const MARKET_TYPE = "margin";
const STOP_PERCENT = 10;
const MARKET_TYPE = "future";
const ASSET = "BTC";
const BASE = "USDT";
const ALLOCATION = 100; //Percentage of our  portfolio to allocate for each trade
const SPREAD = 0.2; //Spread Percentage mid rate Buy or Sell limit order example:  10.000 our sale limit will be 12.000 and buy order will be 8.000
const INTERVAL = 2000; // every 2 seconds evaluate  goig to sell or buy the limit order of the preious ticket  and create new one
const ONLY_CALC = false;
MARKETS = {};
SYMBOL_LEVERAGE = 0;
codeMessage = "";
dynAlloc = 0;
dynSpread = 0;

function signature(query_string) {
  return crypto
    .createHmac("sha256", process.env.API_SECRET)
    .update(query_string)
    .digest("hex");
}

const preData = async (config, binanceClient) => {
  const { asset, base } = config;
  const symbol = `${asset}${base}`;
  // MARKETS = await binanceClient.loadMarkets();
  // MARKET_SYMBOL = await binanceClient.market(symbol);

  // console.log(binanceClient);

  // MARKET_SYMBOL = await binanceClient.fapiPrivatePositionrisk(symbol);
  // MARKET_SYMBOL = await binanceClient.fetchPositions(params);
  params = {
    symbol: symbol,
    limit: "100",
    recvWindow: 9000,
    timestamp: Date.now(),
  };

  const stringified = queryString.stringify(params);
  console.log(stringified);
  cli_signature = signature(stringified);
  params["signature"] = cli_signature;

  // data = requests.get(url, (params = params)).json();
  const result = await Promise.all([
    axios.get(`https://fapi.binance.com/fapi/v2/positionRisk`, {
      apiKey: process.env.API_KEY,
      secret: process.env.API_SECRET,
      verbose: true,
      headers: {
        "X-MBX-APIKEY": process.env.API_KEY,
      },
      params: params,
    }),
    // axios.get(
    //   "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
    //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
    // ),
    // https://fapi.binance.com/fapi/v2/positionRisk?symbol=1000BONKUSDT&timestamp=1702853580832&signature=ca7f9f94abc876aa4fed4cf7b35c311ce935d2abfcbbbbf48293806d1a1313ec
  ]);

  SYMBOL_LEVERAGE = result[0].data[0].leverage;

  console.log(result);
};

const tick = async (config, binanceClient) => {
  const { asset, base, spred, allocation } = config;
  const symbol = `${asset}/${base}`;
  const symbolToRate = symbol.replace("/", "");

  // console.log("MARKET_SYMBOL", MARKET_SYMBOL);

  if (SYMBOL_LEVERAGE > 0) {
    dynAlloc = dynAlloc == 0 ? allocation : dynAlloc;
    dynSpread = dynSpread == 0 ? spred : dynSpread;

    const orders = await binanceClient.fetchOpenOrders(symbol);
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
        `https://fapi.binance.com/fapi/v1/ticker/price?symbol=${symbolToRate}`
      ),
      // axios.get(
      //   "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
      //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
      // ),
      // https://fapi.binance.com/fapi/v2/positionRisk?symbol=1000BONKUSDT&timestamp=1702853580832&signature=ca7f9f94abc876aa4fed4cf7b35c311ce935d2abfcbbbbf48293806d1a1313ec
    ]);

    // result[1] = "0.999809";
    // console.log("Positions:", result[1]);
    result[1] = "1";

    // Give us the Price in the Unit we want
    //const marketPrice = result[0].data.bitcoin.usd / result[1].data.tether.usd;
    const marketPrice = result[0].data.price / result[1];
    // Calulcating the Parameters for the new order
    // const sellPrice = marketPrice * (1 + spred);
    // const buyPrice = marketPrice * (1 - spred);
    const sellPrice = marketPrice + (marketPrice * dynSpread) / 100;
    const buyPrice = marketPrice - (marketPrice * dynSpread) / 100;

    if (codeMessage.indexOf(-2019) > 0) {
      dynAlloc = dynAlloc * 50;
    }

    // Return all the Balance for all Cryptocurrencies
    // const accout = await binanceClient.user();
    const balances = await binanceClient.fetchBalance();
    // Extract the Bitcoin
    const assetBalance = balances.free[asset]; // Initial balance of Bitcoin or USDT
    // Extract Tether
    const baseBalance = balances.free[base]; // Initial balance of Tether
    //Calculates the Sell Volume
    sellVolume = assetBalance / dynAlloc;

    //Calculates the Buy Volume
    const buyVolume = (baseBalance * dynAlloc) / marketPrice;

    sellVolume = sellVolume <= buyVolume ? buyVolume : sellVolume;
    const volume = ((baseBalance * SYMBOL_LEVERAGE) / marketPrice).toFixed(3);

    console.log(`
  	New tick for ${symbol}
  	Created limit sell order for ${volume}@${sellPrice}
  	Created limit buy order for ${volume}@${buyPrice}
  `);

    if (!ONLY_CALC) {
      params = {
        symbol: "BTCUSDT",
        type: "STOP_MARKET",
        side: "SELL",
        positionSide: "BOTH",
        quantity: 0.004,
        reduceOnly: false,
        workingType: "CONTRACT_PRICE",
        priceProtect: true,
        placeType: "order-form",
        stopPrice: ((marketPrice * STOP_PERCENT) / 100).toFixed(1),
        recvWindow: 9000,
        timestamp: Date.now(),
      };

      const stringified = queryString.stringify(params);
      console.log(stringified);
      cli_signature = signature(stringified);
      params["signature"] = cli_signature;

      try {
        order = await binanceClient.createMarketBuyOrder(
          symbol,
          volume,
          buyPrice.toFixed(1),
          ((marketPrice * STOP_PERCENT) / 100).toFixed(1)
        );
        // user was successfully created
        console.log(`Order created BUY ${order}`);
        // business logic goes here
      } catch (error) {
        codeMessage = error.message;
        console.error(error.message); // from creation
      }

      // try {
      //   // data = requests.get(url, (params = params)).json();
      //   order = await axios.get(`https://fapi.binance.com/fapi/v1/order`, {
      //     apiKey: process.env.API_KEY,
      //     secret: process.env.API_SECRET,
      //     verbose: true,
      //     headers: {
      //       "X-MBX-APIKEY": process.env.API_KEY,
      //     },
      //     params: params,
      //   });
      //   console.log(order);
      //   console.log(`
      //   New tick for SELL ${symbol}
      //   Created limit sell order for ${sellVolume}@${sellPrice}
      // `);

      //   // business logic goes here
      // } catch (error) {
      //   console.log(`
      //   New tick for SELL ${symbol}
      //   Created limit sell order for ${sellVolume}@${sellPrice}
      // `);
      //   codeMessage = error.message;
      //   console.error(error.message); // from creation
      // }

      // sideEffectType: "AUTO_BORROW_REPAY",
      // type: "LIMIT",
      // placeType: "order-form",
      // positionSide: "BOTH",
      // reduceOnly:false,

      // "symbol":"BTCUSDT",
      // "type":"STOP_MARKET",
      // "side":"SELL",
      // "positionSide":"BOTH",
      // "quantity":0.004,
      // "reduceOnly":false,
      // "stopPrice":"42990.5",
      // "workingType":"CONTRACT_PRICE",
      // "priceProtect":true,
      // "placeType":"order-form"

      try {
        order = await binanceClient.createMarketSellOrder(
          symbol,
          volume,
          buyPrice.toFixed(1),
          ((marketPrice * STOP_PERCENT) / 100).toFixed(1)
        );
        // user was successfully created
        console.log(`Order created BUY ${order}`);
        // business logic goes here
      } catch (error) {
        codeMessage = error.message;
        console.error(error.message); // from creation
      }
    }
  }
};

const run = () => {
  const config = {
    // asset: "1000BONK",
    // asset: "SEI",
    asset: ASSET,
    base: BASE,
    allocation: ALLOCATION, //Percentage of our  portfolio to allocate for each trade
    spred: SPREAD, //Spread Percentage mid rate Buy or Sell limit order example:  10.000 our sale limit will be 12.000 and buy order will be 8.000
    tickInterval: INTERVAL, // every 2 seconds evaluate  goig to sell or buy the limit order of the preious ticket  and create new one
  };

  const binanceClient = new ccxt.binance({
    apiKey: process.env.API_KEY,
    secret: process.env.API_SECRET,
    verbose: false,
    headers: {
      "X-MBX-APIKEY": process.env.API_KEY,
    },
    options: {
      defaultType: MARKET_TYPE,
    },
  });

  // markets = binanceClient.loadMarkets();
  // market = binanceClient.market(ASSET + BASE);
  // console.log(market);
  // response = exchange.fapiPrivatePostLeverage({
  //   'symbol': market['id'],
  //   'leverage': 1,
  // })

  // console.log(binanceClient);
  // watchPositionForSymbols
  // createMarketSellOrder
  // createMarketBuyOrder
  // createLimitBuyOrder
  // createLimitOrder
  preData(config, binanceClient);
  tick(config, binanceClient);
  setInterval(tick, config.tickInterval, config, binanceClient);
};

// https://api.binance.com/api/v3/openOrders?symbol=BNBUSDT&recvWindow=4000&timestamp={{timestamp}}&signature=95c0a9af68533202da19f7509a08fa8a557da078f87af9d033d0aee017aff79e
run();
