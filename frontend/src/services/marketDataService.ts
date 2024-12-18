
// services/marketDataService.ts
import axios from 'axios'
import type { HistoricalData, TimeFrame, DataSource } from '@/types/market'

interface DataSourceConfig {
  name: DataSource
  baseUrl: string
  apiKey?: string
  rateLimit: number // в миллисекундах
  requiredFields: string[]
}

class MarketDataService {
  private static instance: MarketDataService
  private cache: Map<string, { data: HistoricalData[]; timestamp: number }>
  private lastRequests: Map<DataSource, number>
  private readonly CACHE_DURATION = 24 * 60 * 60 * 1000 // 24 часа

  private dataSources: Record<DataSource, DataSourceConfig> = {
    BINANCE: {
      name: 'BINANCE',
      baseUrl: 'https://api.binance.com/api/v3',
      rateLimit: 1200, // 1.2 секунды между запросами
      requiredFields: ['symbol', 'interval', 'startTime', 'endTime']
    },
    YAHOO: {
      name: 'YAHOO',
      baseUrl: 'https://query1.finance.yahoo.com/v8/finance/chart',
      rateLimit: 2000,
      requiredFields: ['symbol', 'period1', 'period2', 'interval']
    },
    POLYGON: {
      name: 'POLYGON',
      baseUrl: 'https://api.polygon.io/v2',
      apiKey: process.env.VITE_POLYGON_API_KEY,
      rateLimit: 1000,
      requiredFields: ['symbol', 'from', 'to', 'timespan']
    }
  }

  private constructor() {
    this.cache = new Map()
    this.lastRequests = new Map()
  }

  public static getInstance(): MarketDataService {
    if (!MarketDataService.instance) {
      MarketDataService.instance = new MarketDataService()
    }
    return MarketDataService.instance
  }

  /**
   * Получение исторических данных
   */
  public async getHistoricalData(
    symbol: string,
    startDate: string | Date,
    endDate: string | Date,
    timeframe: TimeFrame = '1d',
    source: DataSource = 'BINANCE',
    useCache: boolean = true
  ): Promise<HistoricalData[]> {
    const cacheKey = this.generateCacheKey(symbol, startDate, endDate, timeframe, source)

    // Проверяем кэш
    if (useCache) {
      const cachedData = this.getFromCache(cacheKey)
      if (cachedData) {
        return cachedData
      }
    }

    // Ожидаем соблюдения rate limit
    await this.waitForRateLimit(source)

    try {
      const data = await this.fetchFromSource(source, {
        symbol,
        startDate: new Date(startDate),
        endDate: new Date(endDate),
        timeframe
      })

      // Кэшируем результат
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      })

      return data
    } catch (error) {
      console.error(`Error fetching data from ${source}:`, error)
      throw new Error(`Failed to fetch data from ${source}`)
    }
  }

  /**
   * Получение данных из нескольких источников и их объединение
   */
  public async getMultiSourceData(
    symbol: string,
    startDate: string | Date,
    endDate: string | Date,
    timeframe: TimeFrame = '1d',
    sources: DataSource[] = ['BINANCE', 'YAHOO']
  ): Promise<HistoricalData[]> {
    const promises = sources.map(source =>
      this.getHistoricalData(symbol, startDate, endDate, timeframe, source)
    )

    const results = await Promise.allSettled(promises)
    const validData = results
      .filter((result): result is PromiseFulfilledResult<HistoricalData[]> =>
        result.status === 'fulfilled'
      )
      .map(result => result.value)

    if (validData.length === 0) {
      throw new Error('No data available from any source')
    }

    return this.mergeDataSources(validData)
  }

  /**
   * Проверка доступности данных
   */
  public async checkDataAvailability(
    symbol: string,
    source: DataSource = 'BINANCE'
  ): Promise<{
    available: boolean
    startDate?: Date
    endDate?: Date
    timeframes: TimeFrame[]
  }> {
    try {
      await this.waitForRateLimit(source)
      const info = await this.fetchSymbolInfo(source, symbol)
      return info
    } catch (error) {
      console.error(`Error checking data availability for ${symbol} on ${source}:`, error)
      return {
        available: false,
        timeframes: []
      }
    }
  }

  private async waitForRateLimit(source: DataSource): Promise<void> {
    const lastRequest = this.lastRequests.get(source) || 0
    const rateLimit = this.dataSources[source].rateLimit
    const now = Date.now()
    const timeToWait = Math.max(0, rateLimit - (now - lastRequest))

    if (timeToWait > 0) {
      await new Promise(resolve => setTimeout(resolve, timeToWait))
    }

    this.lastRequests.set(source, Date.now())
  }

  private getFromCache(key: string): HistoricalData[] | null {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data
    }
    return null
  }

  private generateCacheKey(
    symbol: string,
    startDate: string | Date,
    endDate: string | Date,
    timeframe: TimeFrame,
    source: DataSource
  ): string {
    return `${source}:${symbol}:${timeframe}:${new Date(startDate).getTime()}:${new Date(endDate).getTime()}`
  }

  private async fetchFromSource(
    source: DataSource,
    params: {
      symbol: string
      startDate: Date
      endDate: Date
      timeframe: TimeFrame
    }
  ): Promise<HistoricalData[]> {
    const sourceConfig = this.dataSources[source]
    const endpoint = this.buildEndpoint(source, params)
    const headers = this.buildHeaders(source)

    const response = await axios.get(endpoint, { headers })
    return this.parseResponse(source, response.data)
  }

  private buildEndpoint(
    source: DataSource,
    params: {
      symbol: string
      startDate: Date
      endDate: Date
      timeframe: TimeFrame
    }
  ): string {
    switch (source) {
      case 'BINANCE':
        return `${this.dataSources.BINANCE.baseUrl}/klines?symbol=${params.symbol}&interval=${params.timeframe}&startTime=${params.startDate.getTime()}&endTime=${params.endDate.getTime()}`
      case 'YAHOO':
        return `${this.dataSources.YAHOO.baseUrl}/${params.symbol}?period1=${Math.floor(params.startDate.getTime() / 1000)}&period2=${Math.floor(params.endDate.getTime() / 1000)}&interval=${params.timeframe}`
      case 'POLYGON':
        return `${this.dataSources.POLYGON.baseUrl}/aggs/ticker/${params.symbol}/range/1/${params.timeframe}/${params.startDate.toISOString().split('T')[0]}/${params.endDate.toISOString().split('T')[0]}`
      default:
        throw new Error(`Unsupported data source: ${source}`)
    }
  }

  private buildHeaders(source: DataSource): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }

    if (source === 'POLYGON' && this.dataSources.POLYGON.apiKey) {
      headers['X-API-Key'] = this.dataSources.POLYGON.apiKey
    }

    return headers
  }

  private parseResponse(source: DataSource, data: any): HistoricalData[] {
    switch (source) {
      case 'BINANCE':
        return this.parseBinanceData(data)
      case 'YAHOO':
        return this.parseYahooData(data)
      case 'POLYGON':
        return this.parsePolygonData(data)
      default:
        throw new Error(`Unsupported data source: ${source}`)
    }
  }

  private async fetchSymbolInfo(source: DataSource, symbol: string) {
    // Реализация для каждого источника
    switch (source) {
      case 'BINANCE':
        return this.fetchBinanceSymbolInfo(symbol)
      // Добавить другие источники
      default:
        throw new Error(`Unsupported data source: ${source}`)
    }
  }

  // Парсеры для разных источников данных
  private parseBinanceData(data: any[]): HistoricalData[] {
    return data.map(candle => ({
      timestamp: candle[0],
      open: parseFloat(candle[1]),
      high: parseFloat(candle[2]),
      low: parseFloat(candle[3]),
      close: parseFloat(candle[4]),
      volume: parseFloat(candle[5])
    }))
  }

  private parseYahooData(data: any): HistoricalData[] {
    const { timestamp, indicators } = data.chart.result[0]
    const { quote } = indicators

    return timestamp.map((time: number, i: number) => ({
      timestamp: time * 1000,
      open: quote[0].open[i],
      high: quote[0].high[i],
      low: quote[0].low[i],
      close: quote[0].close[i],
      volume: quote[0].volume[i]
    }))
  }

  private parsePolygonData(data: any): HistoricalData[] {
    return data.results.map((result: any) => ({
      timestamp: result.t,
      open: result.o,
      high: result.h,
      low: result.l,
      close: result.c,
      volume: result.v
    }))
  }

  private mergeDataSources(dataSets: HistoricalData[][]): HistoricalData[] {
    // Объединяем данные из разных источников с приоритетом
    const mergedMap = new Map<number, HistoricalData>()

    dataSets.forEach(dataSet => {
      dataSet.forEach(candle => {
        if (!mergedMap.has(candle.timestamp)) {
          mergedMap.set(candle.timestamp, candle)
        }
      })
    })

    return Array.from(mergedMap.values())
      .sort((a, b) => a.timestamp - b.timestamp)
  }
}

export const marketDataService = MarketDataService.getInstance()