// constants/exchange.ts
export const EXCHANGES = {
  BINANCE: 'BINANCE',
  BYBIT: 'BYBIT'
} as const

export type Exchange = typeof EXCHANGES[keyof typeof EXCHANGES]

export const EXCHANGE_NAMES = {
  [EXCHANGES.BINANCE]: 'Binance',
  [EXCHANGES.BYBIT]: 'Bybit'
} as const