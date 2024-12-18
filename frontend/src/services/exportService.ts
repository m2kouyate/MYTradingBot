// services/exportService.ts

import * as XLSX from 'xlsx'
import { jsPDF } from 'jspdf'
import 'jspdf-autotable'
import { formatDate, formatMoney, formatPercent } from '@/utils/formatters'

interface ExportOptions {
  filename: string
  format: 'csv' | 'xlsx' | 'pdf'
  columns: Array<{
    key: string
    label: string
    format?: (value: any) => string
  }>
  onProgress?: (progress: number) => void
}

export class ExportService {
  private static async processDataInChunks<T>(
    data: T[],
    processChunk: (chunk: T[]) => void,
    chunkSize = 1000,
    onProgress?: (progress: number) => void
  ) {
    const totalChunks = Math.ceil(data.length / chunkSize)

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize
      const end = Math.min(start + chunkSize, data.length)
      const chunk = data.slice(start, end)

      await processChunk(chunk)

      if (onProgress) {
        onProgress((i + 1) / totalChunks * 100)
      }
    }
  }

  static async exportData<T>(data: T[], options: ExportOptions): Promise<void> {
    switch (options.format) {
      case 'csv':
        return this.exportToCsv(data, options)
      case 'xlsx':
        return this.exportToXlsx(data, options)
      case 'pdf':
        return this.exportToPdf(data, options)
      default:
        throw new Error(`Unsupported format: ${options.format}`)
    }
  }

  private static async exportToCsv<T>(data: T[], options: ExportOptions): Promise<void> {
    const { columns, filename, onProgress } = options

    // Заголовки
    const headers = columns.map(col => col.label).join(',')
    const rows: string[] = [headers]

    await this.processDataInChunks(data, (chunk) => {
      const chunkRows = chunk.map(item =>
        columns.map(col => {
          const value = item[col.key as keyof T]
          return col.format ? col.format(value) : String(value)
        }).join(',')
      )
      rows.push(...chunkRows)
    }, 1000, onProgress)

    const csv = rows.join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${filename}.csv`
    link.click()
  }

  private static async exportToXlsx<T>(data: T[], options: ExportOptions): Promise<void> {
    const { columns, filename, onProgress } = options

    const wb = XLSX.utils.book_new()
    const ws_data = [columns.map(col => col.label)]

    await this.processDataInChunks(data, (chunk) => {
      const chunkRows = chunk.map(item =>
        columns.map(col => {
          const value = item[col.key as keyof T]
          return col.format ? col.format(value) : value
        })
      )
      ws_data.push(...chunkRows)
    }, 1000, onProgress)

    const ws = XLSX.utils.aoa_to_sheet(ws_data)
    XLSX.utils.book_append_sheet(wb, ws, 'Data')
    XLSX.writeFile(wb, `${filename}.xlsx`)
  }

  private static async exportToPdf<T>(data: T[], options: ExportOptions): Promise<void> {
    const { columns, filename, onProgress } = options

    const doc = new jsPDF()
    const tableData: any[][] = []

    await this.processDataInChunks(data, (chunk) => {
      const chunkRows = chunk.map(item =>
        columns.map(col => {
          const value = item[col.key as keyof T]
          return col.format ? col.format(value) : value
        })
      )
      tableData.push(...chunkRows)
    }, 100, onProgress)

    doc.autoTable({
      head: [columns.map(col => col.label)],
      body: tableData,
      styles: { fontSize: 8 },
      margin: { top: 20 }
    })

    doc.save(`${filename}.pdf`)
  }
}

// Пример использования для экспорта стратегий
export const exportStrategies = async (
  strategies: Strategy[],
  format: 'csv' | 'xlsx' | 'pdf',
  onProgress?: (progress: number) => void
) => {
  const columns = [
    { key: 'name', label: 'Название' },
    { key: 'symbol', label: 'Символ' },
    { key: 'isActive', label: 'Статус', format: (v: boolean) => v ? 'Активна' : 'Неактивна' },
    { key: 'takeProfit', label: 'Take Profit', format: formatPercent },
    { key: 'stopLoss', label: 'Stop Loss', format: formatPercent },
    { key: 'createdAt', label: 'Создана', format: formatDate },
    { key: 'updatedAt', label: 'Обновлена', format: formatDate }
  ]

  await ExportService.exportData(strategies, {
    filename: `strategies_${formatDate(new Date())}`,
    format,
    columns,
    onProgress
  })
}

// Пример использования для экспорта сделок
export const exportTrades = async (
  trades: Trade[],
  format: 'csv' | 'xlsx' | 'pdf',
  onProgress?: (progress: number) => void
) => {
  const columns = [
    { key: 'createdAt', label: 'Дата', format: formatDate },
    { key: 'symbol', label: 'Символ' },
    { key: 'type', label: 'Тип' },
    { key: 'entryPrice', label: 'Цена входа', format: formatMoney },
    { key: 'exitPrice', label: 'Цена выхода', format: (v: number) => v ? formatMoney(v) : '-' },
    { key: 'quantity', label: 'Объём', format: String },
    { key: 'pnl', label: 'P&L', format: formatMoney },
    { key: 'status', label: 'Статус' }
  ]

  await ExportService.exportData(trades, {
    filename: `trades_${formatDate(new Date())}`,
    format,
    columns,
    onProgress
  })
}