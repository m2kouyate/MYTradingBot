// services/marketDataCache.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb'
import type { HistoricalData, DataSource, TimeFrame } from '@/types/market'

interface MarketDataDB extends DBSchema {
  'market-data': {
    key: string
    value: {
      data: HistoricalData[]
      timestamp: number
      source: DataSource
      symbol: string
      timeframe: TimeFrame
      startDate: number
      endDate: number
    }
  }
  'source-configs': {
    key: DataSource
    value: {
      apiKey?: string
      customEndpoint?: string
      lastUpdate: number
    }
  }
}

class MarketDataCache {
  private static instance: MarketDataCache
  private db: IDBPDatabase<MarketDataDB> | null = null
  private readonly DB_NAME = 'market-data-cache'
  private readonly DB_VERSION = 1
  private readonly CACHE_DURATION = 24 * 60 * 60 * 1000 // 24 hours

  private constructor() {}

  public static getInstance(): MarketDataCache {
    if (!MarketDataCache.instance) {
      MarketDataCache.instance = new MarketDataCache()
    }
    return MarketDataCache.instance
  }

  public async initialize(): Promise<void> {
    if (this.db) return

    this.db = await openDB<MarketDataDB>(this.DB_NAME, this.DB_VERSION, {
      upgrade(db) {
        // Хранилище для исторических данных
        db.createObjectStore('market-data')

        // Хранилище для конфигураций источников
        db.createObjectStore('source-configs')
      }
    })
  }

  public async getData(
    source: DataSource,
    symbol: string,
    timeframe: TimeFrame,
    startDate: Date,
    endDate: Date
  ): Promise<HistoricalData[] | null> {
    await this.initialize()
    if (!this.db) return null

    const key = this.generateKey(source, symbol, timeframe, startDate, endDate)
    const cached = await this.db.get('market-data', key)

    if (
      cached &&
      Date.now() - cached.timestamp < this.CACHE_DURATION &&
      this.isDateRangeValid(cached, startDate, endDate)
    ) {
      return cached.data
    }

    return null
  }

  public async setData(
    source: DataSource,
    symbol: string,
    timeframe: TimeFrame,
    startDate: Date,
    endDate: Date,
    data: HistoricalData[]
  ): Promise<void> {
    await this.initialize()
    if (!this.db) return

    const key = this.generateKey(source, symbol, timeframe, startDate, endDate)
    await this.db.put('market-data', {
      data,
      timestamp: Date.now(),
      source,
      symbol,
      timeframe,
      startDate: startDate.getTime(),
      endDate: endDate.getTime()
    }, key)
  }

  public async clearOldCache(): Promise<void> {
    await this.initialize()
    if (!this.db) return

    const now = Date.now()
    const tx = this.db.transaction('market-data', 'readwrite')
    const store = tx.objectStore('market-data')
    const keys = await store.getAllKeys()

    for (const key of keys) {
      const entry = await store.get(key)
      if (entry && now - entry.timestamp > this.CACHE_DURATION) {
        await store.delete(key)
      }
    }
  }

  public async clearCache(): Promise<void> {
    await this.initialize()
    if (!this.db) return

    const tx = this.db.transaction('market-data', 'readwrite')
    await tx.objectStore('market-data').clear()
  }

  private generateKey(
    source: DataSource,
    symbol: string,
    timeframe: TimeFrame,
    startDate: Date,
    endDate: Date
  ): string {
    return `${source}:${symbol}:${timeframe}:${startDate.getTime()}:${endDate.getTime()}`
  }

  private isDateRangeValid(
    cached: MarketDataDB['market-data']['value'],
    startDate: Date,
    endDate: Date
  ): boolean {
    return (
      cached.startDate <= startDate.getTime() &&
      cached.endDate >= endDate.getTime()
    )
  }
}

export const marketDataCache = MarketDataCache.getInstance()