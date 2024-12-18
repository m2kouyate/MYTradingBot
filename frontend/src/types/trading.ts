// types/trading.ts

export interface Strategy {
  id: number;
  name: string;
  symbol: string;
  isActive: boolean;
  buyThreshold: number;
  sellThreshold: number;
  stopLoss: number;
  takeProfit: number;
  createdAt: string;
  updatedAt: string;
}

export interface Trade {
  id: number;
  strategyId: number;
  symbol: string;
  entryPrice: number;
  exitPrice: number | null;
  quantity: number;
  status: 'OPEN' | 'CLOSED';
  pnl: number | null;
  createdAt: string;
  closedAt: string | null;
}

export interface Position {
  id: number;
  strategyId: number;
  symbol: string;
  entryPrice: number;
  currentPrice: number;
  quantity: number;
  unrealizedPnl: number;
  createdAt: string;
}

export interface StrategyStats {
  totalTrades: number;
  winRate: number;
  avgPnl: number;
  totalPnl: number;
  drawdown: number;
}

export interface DashboardStats {
  totalBalance: number;
  activePositions: number;
  todayPnl: number;
  winRate: number;
}

export interface PositionChange {
  id: number
  positionId: number
  type: 'STOP_LOSS' | 'TAKE_PROFIT' | 'PRICE'
  value: number
  timestamp: string
}