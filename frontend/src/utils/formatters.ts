// utils/formatters.ts
export function formatDate(date: string) {
  return new Date(date).toLocaleString()
}

export function formatMoney(amount: number | null) {
  if (amount === null) return '-'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

export function formatPrice(price: number) {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8
  }).format(price)
}

export function formatQuantity(quantity: number) {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8
  }).format(quantity)
}

export function formatPercent(value: number) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value / 100)
}