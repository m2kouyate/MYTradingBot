// utils/patternAnalysis.ts
import type { HistoricalData } from '@/types/market'

export interface PatternMatch {
  pattern: string
  start: number
  end: number
  reliability: number
  signal: 'buy' | 'sell'
  priceTarget?: number
  stopLoss?: number
}

export function findPatterns(data: HistoricalData[]): PatternMatch[] {
  const patterns: PatternMatch[] = []

  patterns.push(
    ...findCandlePatterns(data),
    ...findChartPatterns(data),
    ...findSupportResistance(data)
  )

  return patterns.sort((a, b) => b.reliability - a.reliability)
}

// Основные паттерны для начала
function findCandlePatterns(data: HistoricalData[]): PatternMatch[] {
  const patterns: PatternMatch[] = []

  for (let i = 0; i < data.length - 1; i++) {
    // Doji
    if (isDoji(data[i])) {
      patterns.push({
        pattern: 'Doji',
        start: i,
        end: i,
        reliability: 0.6,
        signal: data[i - 1]?.close < data[i].close ? 'buy' : 'sell'
      })
    }

    // Hammer
    if (isHammer(data[i])) {
      patterns.push({
        pattern: 'Hammer',
        start: i,
        end: i,
        reliability: 0.7,
        signal: 'buy'
      })
    }

    // More patterns...
  }

  return patterns
}