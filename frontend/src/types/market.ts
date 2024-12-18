// types/market.ts

export type TimeFrame = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w'

export type DataSource = 'BINANCE' | 'YAHOO' | 'POLYGON'

export interface HistoricalData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface DataSourceInfo {
  id: DataSource
  name: string
  description: string
  supportedTimeframes: TimeFrame[]
  supportedAssets: ('crypto' | 'stocks' | 'forex')[]
  requiresApiKey: boolean
  rateLimit: {
    requestsPerMinute: number
    requestsPerDay: number
  }
}

export interface DataSourceConfig {
  apiKey?: string
  enabled: boolean
  priority: number
  useCache: boolean
  customEndpoint?: string
}

export interface DataValidationResult {
  isValid: boolean
  issues: {
    type: 'warning' | 'error'
    message: string
  }[]
  coverage: {
    start: Date
    end: Date
    gaps: Array<{ start: Date; end: Date }>
  }
}