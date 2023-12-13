require("dotenv").config({ path: "./.env" });
const ccxt = require("ccxt");
require("axios-debug-log");
const axios = require("axios");

const tick = async (config, binanceClient) => {
  const { asset, base, spred, allocation } = config;
  const market = `${asset}/${base}`;

  const orders = await binanceClient.fetchOpenOrders(market);
  orders.forEach(async (order) => {
    await binanceClient.cancelOrder(order.id);
  });

  const result = await Promise.all([
    axios.get(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    ),
    axios.get(
      "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
    ),
  ]);

  // Give us the Price in the Unit we want
  const marketPrice = result[0].data.bitcoin.usd / result[1].data.tether.usd;
  // Calulcating the Parameters for the new order
  const sellPrice = marketPrice * (1 + spred);
  const buyPrice = marketPrice * (1 - spred);

  // Return all the Balance for all Cryptocurrencies
  const balances = await binanceClient.fetchBalance();
  // Extract the Bitcoin
  const assetBalance = balances.free[asset]; // Initial balance of Bitcoin or USDT
  // Extract Tether
  const baseBalance = balances.free[base]; // Initial balance of Tether
  //Calculates the Sell Volume
  const sellVolume =
    assetBalance > 0 ? assetBalance * allocation : baseBalance * allocation;

  //Calculates the Buy Volume
  const buyVolume = (baseBalance * allocation) / marketPrice;

  console.log(`
  	New tick for ${market}
  	Created limit sell order for ${sellVolume}@${sellPrice}
  	Created limit buy order for ${sellVolume}@${buyPrice}
  `);

  // Sending the Order to Binance
  await binanceClient.createLimitSellOrder(market, sellVolume, sellPrice);
  await binanceClient.createLimitBuyOrder(market, buyVolume, buyPrice);
};

const run = () => {
  const config = {
    asset: "BTC",
    base: "USDT",
    allocation: 0.1, //Percentage of our  portfolio to allocate for each trade
    spred: 0.2, //Spread Percentage mid rate Buy or Sell limit order example:  10.000 our sale limit will be 12.000 and buy order will be 8.000
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
      defaultType: "spot",
      //defaultType: "future",
    },
  });

  tick(config, binanceClient);
  setInterval(tick, config.tickInterval, config, binanceClient);
};
// https://api.binance.com/api/v3/openOrders?symbol=BNBUSDT&recvWindow=4000&timestamp={{timestamp}}&signature=95c0a9af68533202da19f7509a08fa8a557da078f87af9d033d0aee017aff79e
run();
