// services/backtestService.ts
import type { BacktestConfig, BacktestResults } from '@/types/backtest'

interface HistoricalData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface Trade {
  entryDate: number
  entryPrice: number
  exitDate: number
  exitPrice: number
  type: 'BUY' | 'SELL'
  quantity: number
  pnl: number
}

class BacktestService {
  private static instance: BacktestService

  private constructor() {}

  public static getInstance(): BacktestService {
    if (!BacktestService.instance) {
      BacktestService.instance = new BacktestService()
    }
    return BacktestService.instance
  }

  /**
   * Запуск бэктеста
   */
  async runBacktest(
    strategyId: number,
    historicalData: HistoricalData[],
    config: BacktestConfig,
    onProgress?: (progress: number) => void
  ): Promise<BacktestResults> {
    let equity = config.initialCapital
    const trades: Trade[] = []
    const equityCurve: { date: string; equity: number }[] = [{
      date: new Date(historicalData[0].timestamp).toISOString(),
      equity
    }]

    let maxDrawdown = 0
    let highWaterMark = equity
    let currentPosition: Partial<Trade> | null = null

    // Проходим по историческим данным
    for (let i = 1; i < historicalData.length; i++) {
      const candle = historicalData[i]

      // Обновляем прогресс
      if (onProgress) {
        onProgress((i / historicalData.length) * 100)
      }

      // Проверяем сигналы на вход
      if (!currentPosition) {
        const signal = this.checkEntrySignal(
          historicalData.slice(0, i + 1),
          config.parameters
        )

        if (signal) {
          currentPosition = {
            entryDate: candle.timestamp,
            entryPrice: candle.close,
            type: signal,
            quantity: this.calculatePositionSize(equity, candle.close, config)
          }
        }
      }
      // Проверяем условия выхода
      else if (currentPosition) {
        const exitSignal = this.checkExitSignal(
          currentPosition,
          candle,
          config.parameters
        )

        if (exitSignal) {
          const exit: Trade = {
            ...currentPosition as Trade,
            exitDate: candle.timestamp,
            exitPrice: candle.close,
            pnl: this.calculatePnL(
              currentPosition.type!,
              currentPosition.entryPrice!,
              candle.close,
              currentPosition.quantity!,
              config.includeCommissions
            )
          }

          trades.push(exit)
          equity += exit.pnl

          // Обновляем equity curve и drawdown
          equityCurve.push({
            date: new Date(candle.timestamp).toISOString(),
            equity
          })

          if (equity > highWaterMark) {
            highWaterMark = equity
          } else {
            const drawdown = (highWaterMark - equity) / highWaterMark * 100
            maxDrawdown = Math.max(maxDrawdown, drawdown)
          }

          currentPosition = null
        }
      }
    }

    // Рассчитываем статистику
    const results = this.calculateStatistics(
      trades,
      equityCurve,
      maxDrawdown,
      config
    )

    return results
  }

  /**
   * Оптимизация параметров стратегии
   */
  async optimizeParameters(
    historicalData: HistoricalData[],
    config: BacktestConfig,
    onProgress?: (progress: number) => void
  ): Promise<Record<string, number>> {
    const parameterRanges = this.getParameterRanges()
    const results: Array<{ params: Record<string, number>, metrics: BacktestResults }> = []
    let totalIterations = 0
    let currentIteration = 0

    // Рассчитываем общее количество итераций
    for (const param of Object.keys(parameterRanges)) {
      const { min, max, step } = parameterRanges[param]
      totalIterations += Math.floor((max - min) / step) + 1
    }

    // Выполняем оптимизацию для каждого параметра
    for (const param of Object.keys(parameterRanges)) {
      const { min, max, step } = parameterRanges[param]

      for (let value = min; value <= max; value += step) {
        const testConfig = {
          ...config,
          parameters: {
            ...config.parameters,
            [param]: value
          }
        }

        const result = await this.runBacktest(
          0, // временный ID
          historicalData,
          testConfig
        )

        results.push({
          params: { [param]: value },
          metrics: result
        })

        currentIteration++
        if (onProgress) {
          onProgress((currentIteration / totalIterations) * 100)
        }
      }
    }

    // Находим лучшие параметры
    return this.findOptimalParameters(results)
  }

  private checkEntrySignal(
    data: HistoricalData[],
    parameters: Record<string, number>
  ): 'BUY' | 'SELL' | null {
    // Здесь реализуется логика входа в позицию
    // Пример простой стратегии
    const lastCandle = data[data.length - 1]
    const prevCandle = data[data.length - 2]

    if (lastCandle.close > prevCandle.close * (1 + parameters.buyThreshold / 100)) {
      return 'BUY'
    }
    if (lastCandle.close < prevCandle.close * (1 - parameters.sellThreshold / 100)) {
      return 'SELL'
    }

    return null
  }

  private checkExitSignal(
    position: Partial<Trade>,
    currentCandle: HistoricalData,
    parameters: Record<string, number>
  ): boolean {
    const pnlPercent = position.type === 'BUY'
      ? (currentCandle.close - position.entryPrice!) / position.entryPrice! * 100
      : (position.entryPrice! - currentCandle.close) / position.entryPrice! * 100

    return pnlPercent >= parameters.takeProfit || pnlPercent <= -parameters.stopLoss
  }

  private calculatePnL(
    type: 'BUY' | 'SELL',
    entryPrice: number,
    exitPrice: number,
    quantity: number,
    includeCommissions: boolean
  ): number {
    const grossPnl = type === 'BUY'
      ? (exitPrice - entryPrice) * quantity
      : (entryPrice - exitPrice) * quantity

    if (!includeCommissions) {
      return grossPnl
    }

    const commission = (entryPrice + exitPrice) * quantity * 0.001 // 0.1% комиссия
    return grossPnl - commission
  }

  private calculateStatistics(
    trades: Trade[],
    equityCurve: Array<{ date: string; equity: number }>,
    maxDrawdown: number,
    config: BacktestConfig
  ): BacktestResults {
    const winningTrades = trades.filter(t => t.pnl > 0)
    const losingTrades = trades.filter(t => t.pnl < 0)

    const totalPnl = trades.reduce((sum, t) => sum + t.pnl, 0)
    const roi = (totalPnl / config.initialCapital) * 100

    // Рассчитываем коэффициент Шарпа
    const returns = equityCurve.slice(1).map((point, i) =>
      (point.equity - equityCurve[i].equity) / equityCurve[i].equity
    )
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length
    const stdDev = Math.sqrt(
      returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
    )
    const sharpeRatio = avgReturn / stdDev * Math.sqrt(252) // Годовой коэффициент

    return {
      totalPnl,
      roi,
      sharpeRatio,
      maxDrawdown,
      winRate: (winningTrades.length / trades.length) * 100,
      profitFactor: Math.abs(
        winningTrades.reduce((sum, t) => sum + t.pnl, 0) /
        losingTrades.reduce((sum, t) => sum + t.pnl, 0)
      ),
      totalTrades: trades.length,
      equityCurve,
      trades,
      statistics: {
        averageWin: winningTrades.reduce((sum, t) => sum + t.pnl, 0) / winningTrades.length,
        averageLoss: losingTrades.reduce((sum, t) => sum + t.pnl, 0) / losingTrades.length,
        largestWin: Math.max(...winningTrades.map(t => t.pnl)),
        largestLoss: Math.min(...losingTrades.map(t => t.pnl)),
        averageHoldingTime: trades.reduce((sum, t) => sum + (t.exitDate - t.entryDate), 0) / trades.length,
        averageDrawdown: this.calculateAverageDrawdown(equityCurve),
        recoveryFactor: totalPnl / maxDrawdown
      }
    }
  }

  private getParameterRanges() {
    return {
      takeProfit: { min: 0.5, max: 5, step: 0.5 },
      stopLoss: { min: 0.5, max: 5, step: 0.5 },
      buyThreshold: { min: 0.1, max: 2, step: 0.1 },
      sellThreshold: { min: 0.1, max: 2, step: 0.1 }
    }
  }

  private findOptimalParameters(
    results: Array<{ params: Record<string, number>, metrics: BacktestResults }>
  ): Record<string, number> {
    // Сортируем по коэффициенту Шарпа и ROI
    results.sort((a, b) => {
      const scoreA = a.metrics.sharpeRatio * 0.7 + a.metrics.roi * 0.3
      const scoreB = b.metrics.sharpeRatio * 0.7 + b.metrics.roi * 0.3
      return scoreB - scoreA
    })

    return results[0].params
  }

  private calculateAverageDrawdown(
    equityCurve: Array<{ date: string; equity: number }>
  ): number {
    let totalDrawdown = 0
    let drawdownCount = 0
    let peak = equityCurve[0].equity

    for (const point of equityCurve) {
      if (point.equity > peak) {
        peak = point.equity
      } else if (point.equity < peak) {
        totalDrawdown += (peak - point.equity) / peak * 100
        drawdownCount++
      }
    }

    return drawdownCount > 0 ? totalDrawdown / drawdownCount : 0
  }
}

export const backtestService = BacktestService.getInstance()