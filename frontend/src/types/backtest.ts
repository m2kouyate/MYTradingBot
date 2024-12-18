// types/backtest.ts
export interface BacktestConfig {
  startDate: string
  endDate: string
  initialCapital: number
  parameters: {
    takeProfit: number
    stopLoss: number
    // Другие параметры стратегии
    [key: string]: number | string | boolean
  }
  includeCommissions: boolean
  optimizeParameters: boolean
}

export interface BacktestResults {
  totalPnl: number
  roi: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  profitFactor: number
  totalTrades: number
  equityCurve: Array<{
    date: string
    equity: number
  }>
  trades: Array<{
    date: string
    type: 'BUY' | 'SELL'
    entryPrice: number
    exitPrice: number
    quantity: number
    pnl: number
  }>
  statistics: {
    averageWin: number
    averageLoss: number
    largestWin: number
    largestLoss: number
    averageHoldingTime: number
    averageDrawdown: number
    recoveryFactor: number
  }
  optimizedParameters?: {
    takeProfit: number
    stopLoss: number
    [key: string]: number
  }
}