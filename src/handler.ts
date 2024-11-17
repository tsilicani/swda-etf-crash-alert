import yahooFinance from 'yahoo-finance2';

const calculateBollingerBands = (prices: number[], period: number = 10, stdDev: number = 2) => {
  const sma = prices.reduce((a, b) => a + b, 0) / prices.length;
  const squaredDiffs = prices.map(price => Math.pow(price - sma, 2));
  const variance = squaredDiffs.reduce((a, b) => a + b, 0) / prices.length;
  const standardDeviation = Math.sqrt(variance);

  return {
    middle: sma,
    upper: sma + (standardDeviation * stdDev),
    lower: sma - (standardDeviation * stdDev)
  };
};

export const checkBollingerBands = async () => {
  try {
    // Fetch historical data for SWDA.MI
    const result = await yahooFinance.historical('SWDA.MI', {
      period1: new Date(Date.now() - (20 * 24 * 60 * 60 * 1000)), // Last 20 days
      period2: new Date(),
      interval: '1d'
    });

    // Extract closing prices
    const prices = result.map(bar => bar.close);
    const currentPrice = prices[prices.length - 1];

    // Calculate Bollinger Bands for the last 10 days
    const last10Prices = prices.slice(-10);
    const bands = calculateBollingerBands(last10Prices);

    // Calculate and log the difference
    const difference = currentPrice - bands.lower;

    console.log({
      timestamp: new Date().toISOString(),
      currentPrice,
      lowerBand: bands.lower,
      difference,
      message: `Current price is ${difference.toFixed(2)} above the lower Bollinger Band`
    });

    return {
      statusCode: 200,
      body: JSON.stringify({
        currentPrice,
        lowerBand: bands.lower,
        difference
      })
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to process ETF data' })
    };
  }
};
