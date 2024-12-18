// utils/indicators.ts
import { HistoricalData } from '@/types/market'

interface IndicatorResult {
  timestamp: number
  value: number
}

export function calculateIndicators(
  data: HistoricalData[],
  indicator: string,
  period: number = 14
): IndicatorResult[] {
  switch (indicator) {
    case 'sma':
      return calculateSMA(data, period)
    case 'ema':
      return calculateEMA(data, period)
    case 'bollinger':
      return calculateBollingerBands(data, period)
    default:
      return []
  }
}

export function calculateSMA(
  data: HistoricalData[],
  period: number
): IndicatorResult[] {
  const results: IndicatorResult[] = []

  for (let i = period - 1; i < data.length; i++) {
    const sum = data
      .slice(i - period + 1, i + 1)
      .reduce((acc, candle) => acc + candle.close, 0)

    results.push({
      timestamp: data[i].timestamp,
      value: sum / period
    })
  }

  return results
}

export function calculateEMA(
  data: HistoricalData[],
  period: number
): IndicatorResult[] {
  const results: IndicatorResult[] = []
  const multiplier = 2 / (period + 1)

  let ema = data[0].close
  results.push({
    timestamp: data[0].timestamp,
    value: ema
  })

  for (let i = 1; i < data.length; i++) {
    ema = (data[i].close - ema) * multiplier + ema
    results.push({
      timestamp: data[i].timestamp,
      value: ema
    })
  }

  return results
}

export function calculateBollingerBands(
  data: HistoricalData[],
  period: number,
  stdDev: number = 2
): IndicatorResult[] {
  const sma = calculateSMA(data, period)
  const results: IndicatorResult[] = []

  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1)
    const variance = slice.reduce((sum, candle) => {
      const diff = candle.close - sma[i - (period - 1)].value
      return sum + diff * diff
    }, 0) / period

    const std = Math.sqrt(variance)
    const upperBand = sma[i - (period - 1)].value + stdDev * std
    const lowerBand = sma[i - (period - 1)].value - stdDev * std

    results.push({
      timestamp: data[i].timestamp,
      value: upperBand
    })
  }

  return results
}