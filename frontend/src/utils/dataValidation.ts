// utils/dataValidation.ts
import type { HistoricalData } from '@/types/market'

interface ValidationIssue {
  type: 'error' | 'warning'
  message: string
  affectedData?: {
    index: number
    timestamp: number
  }
}

interface ValidationResult {
  isValid: boolean
  issues: ValidationIssue[]
  coverage: {
    start: Date
    end: Date
    gaps: Array<{ start: Date; end: Date }>
  }
  statistics: {
    totalCandles: number
    validCandles: number
    anomalies: number
    gapCount: number
    consistencyScore: number
  }
}

export function validateHistoricalData(data: HistoricalData[]): ValidationResult {
  const issues: ValidationIssue[] = []
  let validCandles = 0
  let anomalies = 0

  // Проверка базовой валидности
  if (!Array.isArray(data) || data.length === 0) {
    return {
      isValid: false,
      issues: [{
        type: 'error',
        message: 'Данные отсутствуют или имеют неверный формат'
      }],
      coverage: {
        start: new Date(),
        end: new Date(),
        gaps: []
      },
      statistics: {
        totalCandles: 0,
        validCandles: 0,
        anomalies: 0,
        gapCount: 0,
        consistencyScore: 0
      }
    }
  }

  // Проверка сортировки по времени
  if (!isChronologicalOrder(data)) {
    issues.push({
      type: 'error',
      message: 'Данные не отсортированы по времени'
    })
  }

  // Поиск пропусков в данных
  const gaps = findDataGaps(data)
  gaps.forEach(gap => {
    issues.push({
      type: 'warning',
      message: `Пропуск данных с ${formatDate(gap.start)} по ${formatDate(gap.end)}`
    })
  })

  // Проверка каждой свечи
  data.forEach((candle, index) => {
    const candleIssues = validateCandle(candle, index)
    if (candleIssues.length === 0) {
      validCandles++
    } else {
      issues.push(...candleIssues)
      if (candleIssues.some(issue => issue.type === 'error')) {
        anomalies++
      }
    }
  })

  // Проверка объемов
  const volumeIssues = validateVolumes(data)
  issues.push(...volumeIssues)

  // Проверка ценовых аномалий
  const priceIssues = validatePrices(data)
  issues.push(...priceIssues)

  // Расчет итоговой статистики
  const consistencyScore = calculateConsistencyScore({
    totalCandles: data.length,
    validCandles,
    anomalies,
    gapCount: gaps.length
  })

  return {
    isValid: issues.filter(i => i.type === 'error').length === 0,
    issues,
    coverage: {
      start: new Date(data[0].timestamp),
      end: new Date(data[data.length - 1].timestamp),
      gaps
    },
    statistics: {
      totalCandles: data.length,
      validCandles,
      anomalies,
      gapCount: gaps.length,
      consistencyScore
    }
  }
}

function validateCandle(
  candle: HistoricalData,
  index: number
): ValidationIssue[] {
  const issues: ValidationIssue[] = []

  // Проверка структуры свечи
  if (!isValidCandleStructure(candle)) {
    issues.push({
      type: 'error',
      message: `Неверная структура свечи на индексе ${index}`,
      affectedData: { index, timestamp: candle.timestamp }
    })
    return issues
  }

  // Проверка логики цен
  if (candle.high < candle.low) {
    issues.push({
      type: 'error',
      message: `High меньше Low на индексе ${index}`,
      affectedData: { index, timestamp: candle.timestamp }
    })
  }

  if (candle.open > candle.high || candle.open < candle.low) {
    issues.push({
      type: 'error',
      message: `Open выходит за пределы High/Low на индексе ${index}`,
      affectedData: { index, timestamp: candle.timestamp }
    })
  }

  if (candle.close > candle.high || candle.close < candle.low) {
    issues.push({
      type: 'error',
      message: `Close выходит за пределы High/Low на индексе ${index}`,
      affectedData: { index, timestamp: candle.timestamp }
    })
  }

  // Проверка нулевых объемов
  if (candle.volume === 0) {
    issues.push({
      type: 'warning',
      message: `Нулевой объем на индексе ${index}`,
      affectedData: { index, timestamp: candle.timestamp }
    })
  }

  return issues
}

function validateVolumes(data: HistoricalData[]): ValidationIssue[] {
  const issues: ValidationIssue[] = []
  const volumes = data.map(c => c.volume)
  const avgVolume = volumes.reduce((a, b) => a + b) / volumes.length
  const stdDev = calculateStdDev(volumes)

  data.forEach((candle, index) => {
    // Проверка аномальных объемов (более 5 стандартных отклонений)
    if (candle.volume > avgVolume + stdDev * 5) {
      issues.push({
        type: 'warning',
        message: `Аномально высокий объем на индексе ${index}`,
        affectedData: { index, timestamp: candle.timestamp }
      })
    }

    // Проверка последовательности нулевых объемов
    if (index > 0 && index < data.length - 1) {
      if (
        candle.volume === 0 &&
        data[index - 1].volume === 0 &&
        data[index + 1].volume === 0
      ) {
        issues.push({
          type: 'warning',
          message: `Последовательность нулевых объемов начиная с индекса ${index - 1}`,
          affectedData: { index, timestamp: candle.timestamp }
        })
      }
    }
  })

  return issues
}

function validatePrices(data: HistoricalData[]): ValidationIssue[] {
  const issues: ValidationIssue[] = []
  const closes = data.map(c => c.close)
  const avgPrice = closes.reduce((a, b) => a + b) / closes.length
  const stdDev = calculateStdDev(closes)

  data.forEach((candle, index) => {
    // Проверка резких изменений цены
    if (index > 0) {
      const priceChange = Math.abs(candle.close - data[index - 1].close)
      const changePercent = (priceChange / data[index - 1].close) * 100

      if (changePercent > 20) { // Более 20% изменения
        issues.push({
          type: 'warning',
          message: `Резкое изменение цены (${changePercent.toFixed(2)}%) на индексе ${index}`,
          affectedData: { index, timestamp: candle.timestamp }
        })
      }
    }

    // Проверка аномальных цен
    if (Math.abs(candle.close - avgPrice) > stdDev * 5) {
      issues.push({
        type: 'warning',
        message: `Аномальная цена на индексе ${index}`,
        affectedData: { index, timestamp: candle.timestamp }
      })
    }
  })

  return issues
}

// Вспомогательные функции
function isChronologicalOrder(data: HistoricalData[]): boolean {
  for (let i = 1; i < data.length; i++) {
    if (data[i].timestamp <= data[i - 1].timestamp) {
      return false
    }
  }
  return true
}

function findDataGaps(
  data: HistoricalData[]
): Array<{ start: Date; end: Date }> {
  const gaps: Array<{ start: Date; end: Date }> = []
  const expectedInterval = getExpectedInterval(data)

  for (let i = 1; i < data.length; i++) {
    const timeDiff = data[i].timestamp - data[i - 1].timestamp
    if (timeDiff > expectedInterval * 1.5) { // 50% больше ожидаемого интервала
      gaps.push({
        start: new Date(data[i - 1].timestamp),
        end: new Date(data[i].timestamp)
      })
    }
  }

  return gaps
}

function getExpectedInterval(data: HistoricalData[]): number {
  // Определяем наиболее частый интервал между свечами
  const intervals: number[] = []
  for (let i = 1; i < Math.min(100, data.length); i++) {
    intervals.push(data[i].timestamp - data[i - 1].timestamp)
  }
  return findMode(intervals)
}

function calculateConsistencyScore(stats: {
  totalCandles: number
  validCandles: number
  anomalies: number
  gapCount: number
}): number {
  const validityScore = stats.validCandles / stats.totalCandles
  const anomalyPenalty = stats.anomalies / stats.totalCandles
  const gapPenalty = stats.gapCount / stats.totalCandles

  return Math.max(0, Math.min(100,
    (validityScore - anomalyPenalty - gapPenalty) * 100
  ))
}

// ... другие вспомогательные функции