/**
 * Type definitions for ETF data structures
 */

// Constituent data with latest price
export interface ConstituentData {
  symbol: string;
  weight: number;
  latest_price: number;
}

// Time series data point
export interface TimeSeriesData {
  date: string;
  price: number;
}

// Top holding data
export interface TopHoldingData {
  symbol: string;
  weight: number;
  latest_price: number;
  holding_value: number;
}

// API response from POST /api/py/v1/etfs endpoint
export interface ETFDataResponse {
  status: string;
  table_data: ConstituentData[];
  time_series: TimeSeriesData[];
  top_holdings: TopHoldingData[];
}

