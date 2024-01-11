require("dotenv").config({ path: "./.env" });
const crypto = require("crypto");
const tulind = require("tulind");
var talib = require("ta-lib");

//Tulind Functions
const {
  sma_inc,
  ema_inc,
  markers_inc,
  rsi_inc,
  macd_inc,
} = require("./indicators");
const log = console.log;

// var W3CWebSocket = require("websocket").w3cwebsocket;
const ccxt = require("ccxt");
const queryString = require("querystring");
require("axios-debug-log");
const axios = require("axios");

// const MARKET_TYPE = "spot";
// const MARKET_TYPE = "margin";
const STOP_PERCENT = 0.95;
const MARKET_TYPE = "future";
const ASSET = "BTC";
const BASE = "USDT";
const ALLOCATION = 100; //Percentage of our  portfolio to allocate for each trade
const SPREAD = 0.2; //Spread Percentage mid rate Buy or Sell limit order example:  10.000 our sale limit will be 12.000 and buy order will be 8.000
const INTERVAL = 1000; // every 2 seconds evaluate  goig to sell or buy the limit order of the preious ticket  and create new one
const ONLY_CALC = false;
MARKETS = {};
SYMBOL_LEVERAGE = 0;
SYMBOL_TICKER = (0.0001 + "").split(".")[1].length;
codeMessage = "";
dynAlloc = 0;
dynSpread = 0;
klines = [];

RSI_PERIOD = 14;
RSI_OVERBOUGHT = 70;
RSI_OVERSOLD = 30;
IN_POSITION = false;
ORDER_SUCCEEDED = false;
closesArray = [];
CLOSE_TIME_START = 1;
CLOSE_TIME_END = 59;
AUTH_TO_BUY = false;
AUTH_TO_SELL = false;

function calculateRSI(closingPrices) {
  // Calculate the average of the upward price changes
  let avgUpwardChange = 0;
  for (let i = 1; i < closingPrices.length; i++) {
    avgUpwardChange += Math.max(0, closingPrices[i] - closingPrices[i - 1]);
  }
  avgUpwardChange /= closingPrices.length;

  // Calculate the average of the downward price changes
  let avgDownwardChange = 0;
  for (let i = 1; i < closingPrices.length; i++) {
    avgDownwardChange += Math.max(0, closingPrices[i - 1] - closingPrices[i]);
  }
  avgDownwardChange /= closingPrices.length;

  // Calculate the RSI
  const rsi = 100 - 100 / (1 + avgUpwardChange / avgDownwardChange);

  log("Manual Last RSI: ", rsi);

  return rsi;
}

// Array.prototype.insert = function (index, ...items) {
//   this.splice(index, 0, ...items);
// };

function signature(query_string) {
  return crypto
    .createHmac("sha256", process.env.API_SECRET)
    .update(query_string)
    .digest("hex");
}

function filter_data_per_time(klines, secondLoad) {
  date = new Date();
  seconds = date.getSeconds();
  // console.log(seconds);

  if (seconds >= CLOSE_TIME_START && seconds <= CLOSE_TIME_END) {
    console.log(
      `======= ======= Catch Seconds between ${CLOSE_TIME_START} and ${CLOSE_TIME_END} ======= =======`
    );

    klines[klines.length - 1].forEach((f) => {
      mseconds = date.getMilliseconds();
      console.log(
        `Times: ${seconds}:${mseconds} open: ${f.open} high: ${f.high} low: ${f.low} close: ${f.close}: ${f.close}`
      );
    });

    console.log("======= ======= end of chunck ======= =======");

    // closesArray.push(klines[klines.length - 1].map((f) => f.close));
    // Oly Gets the Closes Times between 15 and 45 seconds
    // closesArray.push(
    //   klines[klines.length - 1]
    //     .map((f) => f.close)

    // );
    // var array = [['TEST1'], ['TEST2'], ['TEST3'], ['TEST4'], ['TEST5']];
    // [].concat.apply([], array);
    // if (!secondLoad) {
    closesArray = closesArray.concat.apply(
      [],
      klines[klines.length - 1].map((f) => f.close)
    );
    // }

    // if (secondLoad) {
    //   closesArray.push[closesArray.length - 1] =
    //     klines[klines.length - 1][klines[0].length - 1].close;
    // }

    // if (secondLoad) {
    //   leftRotateByOne(closesArray);
    //   closesArray[closesArray.length - 1] =
    //     klines[klines.length - 1][klines[0].length - 1].close;
    // }

    // log(`Closes tt: ${closesArray.length}`, closesArray);
  }
}

function leftRotateByOne(arr) {
  if (arr.length <= 1) {
    return arr;
  }

  let elem1 = arr.shift();
  arr.push(elem1);

  return arr;
}

const preData = async (config, binanceClient) => {
  const { asset, base } = config;
  const symbol = `${asset}${base}`;
  // MARKETS = await binanceClient.loadMarkets();
  // MARKET_SYMBOL = await binanceClient.market(symbol);

  // console.log(binanceClient);

  // MARKET_SYMBOL = await binanceClient.fapiPrivatePositionrisk(symbol);
  // MARKET_SYMBOL = await binanceClient.fetchPositions(params);
  params_1 = {
    symbol: symbol,
    limit: "10",
    recvWindow: 15000,
    timestamp: Date.now(),
  };

  params_kline = {
    symbol: symbol,
    interval: "1m",
    limit: "60",
    recvWindow: 10000,
    timestamp: Date.now(),
  };

  var stringified = queryString.stringify(params_1);
  cli_signature = signature(stringified);
  params_1["signature"] = cli_signature;

  stringified = queryString.stringify(params_kline);
  cli_signature = signature(stringified);
  params_kline["signature"] = cli_signature;

  // data = requests.get(url, (params = params)).json();
  const result = await Promise.all([
    axios.get(`https://fapi.binance.com/fapi/v2/positionRisk`, {
      apiKey: process.env.API_KEY,
      secret: process.env.API_SECRET,
      verbose: true,
      headers: {
        "X-MBX-APIKEY": process.env.API_KEY,
      },
      params: params_1,
    }),
    axios.get(`https://fapi.binance.com/fapi/v1/klines`, {
      apiKey: process.env.API_KEY,
      secret: process.env.API_SECRET,
      verbose: true,
      headers: {
        "X-MBX-APIKEY": process.env.API_KEY,
      },
      params: params_kline,
    }),
    // https://fapi.binance.com/fapi/v2/positionRisk?symbol=1000BONKUSDT&timestamp=1702853580832&signature=ca7f9f94abc876aa4fed4cf7b35c311ce935d2abfcbbbbf48293806d1a1313ec
  ]);

  SYMBOL_LEVERAGE = result[0].data[0].leverage;

  console.log("POSITION RISK: \n", result[0]);
  console.log("KLINES: \n", result[1]);

  // const data = JSON.parse(result[1].data);
  let klinedata = result[1].data.map((d) => ({
    time: d[0] / 1000,
    open: d[1] * 1,
    high: d[2] * 1,
    low: d[3] * 1,
    close: d[4] * 1,
  }));

  klinedata = await sma_inc(klinedata);
  klinedata = await ema_inc(klinedata);
  klinedata = markers_inc(klinedata);
  klinedata = await rsi_inc(klinedata);
  klinedata = await macd_inc(klinedata);

  klines.push(klinedata);
  // console.log("KLINES DATA: \n", klines);

  filter_data_per_time(klines, false);

  // Example usage
  // const closingPrices = [100, 110, 105, 115, 120, 130, 140, 150, 145, 155];
  // const last_rsi = calculateRSI(closingPrices);
  // console.log("LAST RSI: ", last_rsi); // Output: 71.43

  if (closesArray.length > RSI_PERIOD) {
    last_tulind = 0.0;
    tulind.indicators.rsi.indicator(
      [klinedata.map((f) => f.close)],
      [14],
      (err, res) => {
        if (err) return log(err);
        last_tulind = res[0].slice(-1)[0];
        log("Tulind RSI: ", last_tulind);
      }
    );
    log("RSI : ", klinedata[klinedata.length - 1].rsi);
    log("EMA : ", klinedata[klinedata.length - 1].ema);
    log("MSA : ", klinedata[klinedata.length - 1].msa);
    log("MACD : ", klinedata[klinedata.length - 1].macd);
    const last_rsi = calculateRSI(closesArray);

    talibRS_1 = talib.RSI(closesArray, 14);
    talibRS_2 = talib.RSI(
      klinedata.map((f) => f.close),
      14
    );
    log("RSI TA-LIB 1: ", talibRS_1[talibRS_1.length - 1]);
    log("RSI TA-LIB 2: ", talibRS_2[talibRS_2.length - 1]);

    calling_bot_decision(last_rsi);

    if (last_rsi > RSI_OVERBOUGHT) {
      console.log("Overbought! Sell! Sell! Sell!");
    }

    if (last_rsi < RSI_OVERSOLD) {
      console.log("Overbought! Sell! Sell! Sell!");
      console.log("Oversold! Buy! Buy! Buy!");
    }
  }

  // const open = require("./data").data.map((d) => d[1]);
  // const high = require("./data").data.map((d) => d[2]);
  // const low = require("./data").data.map((d) => d[3]);
  // const close = require("./data").data.map((d) => d[4]);
};

function calling_bot_decision(last_rsi) {
  if (last_rsi > RSI_OVERBOUGHT) {
    if (IN_POSITION) {
      console.log("Overbought! Sell! Sell! Sell!");
      // put binance sell logic here
      // order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
      if (ORDER_SUCCEEDED) IN_POSITION = False;
    } else {
      console.log("It is overbought, but we don't own any. Nothing to do.");
    }
  }

  if (last_rsi < RSI_OVERSOLD) {
    if (IN_POSITION)
      console.log("It is oversold, but you already own it, nothing to do.");
    else {
      console.log("Oversold! Buy! Buy! Buy!");
      // put binance buy order logic here
      // order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
      if (ORDER_SUCCEEDED) in_position = True;
    }
  }
}

orders = [];

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

    params_kline = {
      symbol: symbolToRate,
      interval: "1m",
      limit: "60",
      recvWindow: 10000,
      timestamp: Date.now(),
    };

    stringified = queryString.stringify(params_kline);
    cli_signature = signature(stringified);
    params_kline["signature"] = cli_signature;

    const result = await Promise.all([
      axios.get(
        `https://fapi.binance.com/fapi/v1/ticker/price?symbol=${symbolToRate}`
      ),
      axios.get(`https://fapi.binance.com/fapi/v1/klines`, {
        apiKey: process.env.API_KEY,
        secret: process.env.API_SECRET,
        verbose: true,
        headers: {
          "X-MBX-APIKEY": process.env.API_KEY,
        },
        params: params_kline,
      }),
      // axios.get(
      //   "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
      //   // "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"
      // ),
      // https://fapi.binance.com/fapi/v2/positionRisk?symbol=1000BONKUSDT&timestamp=1702853580832&signature=ca7f9f94abc876aa4fed4cf7b35c311ce935d2abfcbbbbf48293806d1a1313ec
    ]);

    // result[1] = "0.999809";
    // console.log("Positions:", result[1]);
    result[2] = "1";

    // const data = JSON.parse(result[1].data);
    let klinedata = result[1].data.map((d) => ({
      time: d[0] / 1000,
      open: d[1] * 1,
      high: d[2] * 1,
      low: d[3] * 1,
      close: d[4] * 1,
    }));

    klinedata = await sma_inc(klinedata);
    klinedata = await ema_inc(klinedata);
    klinedata = markers_inc(klinedata);
    klinedata = await rsi_inc(klinedata);
    klinedata = await macd_inc(klinedata);

    klines.push(klinedata);
    filter_data_per_time(klines, true);

    if (closesArray.length > RSI_PERIOD) {
      last_tulind = 0.0;
      tulind.indicators.rsi.indicator(
        [klinedata.map((f) => f.close)],
        [14],
        (err, res) => {
          if (err) return log(err);
          last_tulind = res[0].slice(-1)[0];
          log("Tulind RSI: ", last_tulind);
        }
      );
      log("RSI : ", klinedata[klinedata.length - 1].rsi);
      log("EMA : ", klinedata[klinedata.length - 1].ema);
      log("MSA : ", klinedata[klinedata.length - 1].msa);
      log("MACD : ", klinedata[klinedata.length - 1].macd);
      const last_rsi = calculateRSI(closesArray);

      talibRS_1 = talib.RSI(closesArray, 14);
      talibRS_2 = talib.RSI(
        klinedata.map((f) => f.close),
        14
      );
      log("RSI TA-LIB 1: ", talibRS_1[talibRS_1.length - 1]);
      log("RSI TA-LIB 2: ", talibRS_2[talibRS_2.length - 1]);

      calling_bot_decision(last_rsi);
    }

    // Give us the Price in the Unit we want
    //const marketPrice = result[0].data.bitcoin.usd / result[1].data.tether.usd;
    const marketPrice = result[0].data.price / result[2];
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
    const volume = ((baseBalance * SYMBOL_LEVERAGE) / marketPrice).toFixed(
      SYMBOL_TICKER
    );

    //   console.log(`
    // 	New tick for ${symbol}
    // 	Created limit sell order for ${volume}@${sellPrice}
    // 	Created limit buy order for ${volume}@${buyPrice}
    // `);

    if (!ONLY_CALC) {
      // params = {
      //   symbol: "BTCUSDT",
      //   type: "STOP_MARKET",
      //   side: "SELL",
      //   positionSide: "BOTH",
      //   quantity: 0.004,
      //   reduceOnly: false,
      //   workingType: "CONTRACT_PRICE",
      //   priceProtect: true,
      //   placeType: "order-form",
      //   stopPrice: ((marketPrice * STOP_PERCENT) / 100).toFixed(SYMBOL_TICKER),
      //   recvWindow: 9000,
      //   timestamp: Date.now(),
      // };

      // const stringified = queryString.stringify(params);
      // console.log(stringified);
      // cli_signature = signature(stringified);
      // params["signature"] = cli_signature;

      buyStopLimit = (
        parseFloat(marketPrice) +
        parseFloat(((marketPrice * 0.8) / 100).toFixed(SYMBOL_TICKER))
      ).toFixed(SYMBOL_TICKER);

      sellStopLimit = (
        parseFloat(marketPrice) -
        parseFloat(((marketPrice * 0.8) / 100).toFixed(SYMBOL_TICKER))
      ).toFixed(SYMBOL_TICKER);

      if (AUTH_TO_BUY) {
        try {
          order = await binanceClient.createMarketBuyOrder(
            symbol,
            volume,
            buyPrice.toFixed(SYMBOL_TICKER),
            buyStopLimit
          );
          // user was successfully created
          console.log(`Order created BUY ${order}`);
          orders.push(order);
          // business logic goes here
        } catch (error) {
          codeMessage = error.message;
          console.error(error.message); // from creation
          console.log(`
            TRIED TO BUY ${symbol}
            Quantity : ${volume}
            Buy Price: ${buyPrice.toFixed(SYMBOL_TICKER)}
            Stop Limit: ${buyStopLimit}
          `);
        }
      }

      if (AUTH_TO_SELL) {
        try {
          order = await binanceClient.createMarketSellOrder(
            symbol,
            volume,
            sellPrice.toFixed(SYMBOL_TICKER),
            sellStopLimit
          );
          // user was successfully created
          console.log(`Order created SELL ${order}`);
          orders.push(order);
          // business logic goes here
        } catch (error) {
          codeMessage = error.message;
          console.error(error.message); // from creation
          console.log(`
            TRIED TO SELL ${symbol}
            Quantity : ${volume}
            Buy Price: ${sellPrice.toFixed(SYMBOL_TICKER)}
            Stop Limit: ${sellStopLimit}
          `);
        }
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
