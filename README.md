# ETF Price Monitor

A single-page web application for viewing historical ETF prices and analyzing top holdings.

## Quick Start

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.10+

### Installation & Running

1. **Clone and navigate to the project**
```bash
cd ETF_Price_Monitor
```

2. **Set up Python virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install all dependencies and start development servers**
```bash
npm install
npm run dev
```

This single command will:
- Install Python dependencies from `requirements.txt`
- Install Node.js dependencies
- Start FastAPI backend on port 8000
- Start Next.js frontend on port 3000

4. **Access the application**
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000/api/py/docs](http://localhost:8000/api/py/docs)

---

## Features

### Implemented Requirements
- **CSV Upload**: Upload `ETF1.csv` or `ETF2.csv` to configure ETF constituents
- **Interactive Table**: 
  - Displays constituent symbol, weight, and latest price
  - Sortable columns (ascending/descending)
  - Pagination (10 items per page)
- **Time Series Chart**: Zoomable line chart showing reconstructed ETF price history
- **Top 5 Holdings**: Bar chart displaying largest holdings by market value (weight × price)

---

## Architecture

### Technology Stack

**Frontend**
- **Next.js 16** (App Router) - React framework with SSR capabilities
- **TypeScript** - Type safety and better developer experience
- **shadcn/ui** - Modern, accessible UI components
- **Recharts** - Declarative charting library for React
- **Tailwind CSS** - Utility-first styling

**Backend**
- **FastAPI** - High-performance Python web framework
- **Pandas** - Data manipulation and analysis
- **Uvicorn** - ASGI server for FastAPI

### System Design

```
┌─────────────────────────────────────────┐
│  Browser (Next.js Frontend)             │
│  ├─ FileUpload Component                │
│  ├─ ETFTable (sortable, paginated)      │
│  ├─ TimeSeriesChart (zoomable)          │
│  └─ TopHoldingsChart                    │
└────────────┬────────────────────────────┘
             │ HTTP/REST
             ▼
┌─────────────────────────────────────────┐
│  FastAPI Backend                         │
│  ├─ POST /api/py/v1/etfs                │
│  │   ├─ Validate CSV format             │
│  │   ├─ Calculate ETF prices            │
│  │   └─ Compute top holdings            │
│  └─ GET /api/py/v1/health               │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  Data Layer (Pandas)                     │
│  ├─ prices.csv (cached at startup)      │
│  ├─ ETF calculation service             │
│  └─ Historical price lookup             │
└─────────────────────────────────────────┘
```

---

## Core Logic

### ETF Price Calculation
```
ETF_price(t) = Σ (weight_i × constituent_price_i(t))
```

### Holding Value Calculation
```
holding_value_i = weight_i × latest_price_i
```

### Data Processing
- **Forward-fill** missing prices with last known value
- **Backward-fill** any remaining leading NaN values
- Constituents matched by symbol name across datasets

---

## API Documentation

### `POST /api/py/v1/etfs`

**Request**: `multipart/form-data`
```
file: ETF[1-2].csv
```

**Response**: `application/json`
```json
{
  "status": "success",
  "table_data": [
    {
      "symbol": "A",
      "weight": 0.02,
      "latest_price": 20.05
    }
  ],
  "time_series": [
    {
      "date": "2017-01-01",
      "price": 150.23
    }
  ],
  "top_holdings": [
    {
      "symbol": "B",
      "weight": 0.15,
      "latest_price": 50.25,
      "holding_value": 7.5375
    }
  ]
}
```

---

## Design Decisions

### 1. Frontend Architecture
- **Single Page Application**: All components on one page for better UX
- **Client-Side Rendering**: Charts and tables rendered in browser for interactivity
- **Component-Based**: Modular design with reusable UI components

### 2. Backend Architecture
- **Modular Structure**: Separated routers, services, and data layers
- **Data Caching**: `prices.csv` loaded once at startup (100 rows cached in memory)
- **Dependency Injection**: Services instantiated via FastAPI's DI system

### 3. Data Processing
- **Stateless API**: No session storage; ETF config provided with each request
- **Vectorized Operations**: Pandas used for efficient time-series calculations
- **Error Handling**: Validation for CSV format, missing constituents, and data integrity

### 4. UI/UX Enhancements
- **Responsive Design**: Works on desktop and tablet screens
- **Interactive Elements**: Sortable tables, paginated views, zoomable charts
- **Feedback**: Success/error alerts with auto-dismiss

---

## Assumptions

1. **Data Quality**
   - All constituents in `ETF[1-2].csv` have corresponding price data in `prices.csv`
   - Date columns are properly formatted (`YYYY-MM-DD`)

2. **Business Logic**
   - ETF weights remain constant over the entire time period
   - Holding value = weight × latest closing price (not market cap)
   - "Latest price" refers to the most recent date in `prices.csv`

3. **Scope**
   - Single user, no authentication required
   - No data persistence (stateless application)
   - CSV files are well-formed and trusted input

4. **Technical**
   - Backend and frontend run on separate ports (development mode)
   - CORS enabled for local development
   - Historical data fits in memory (~100 rows × 40 constituents)

---

## Project Structure

```
ETF_Price_Monitor/
├── app/                      # Next.js frontend
│   ├── page.tsx              # Main application page
│   ├── layout.tsx            # Root layout with metadata
│   └── globals.css           # Global styles and theme
├── components/               # React components
│   ├── FileUpload.tsx        # CSV upload component
│   ├── ETFTable.tsx          # Interactive data table
│   ├── TimeSeriesChart.tsx   # Zoomable line chart
│   ├── TopHoldingsChart.tsx  # Bar chart for top 5
│   └── ui/                   # shadcn/ui components
├── lib/                      # Utilities and types
│   ├── types.ts              # TypeScript interfaces
│   └── utils.ts              # Helper functions
├── api/                      # FastAPI backend
│   ├── index.py              # Main FastAPI app
│   ├── routers/              # API route handlers
│   │   └── etf_router.py     # ETF endpoints
│   └── services/             # Business logic
│       ├── data_loader.py    # Singleton data cache
│       └── calculator.py     # ETF calculations
├── data/                     # Sample data
│   ├── ETF1.csv              # Sample ETF config
│   ├── ETF2.csv              # Sample ETF config
│   └── prices.csv            # Historical prices
└── requirements.txt          # Python dependencies
```

---

## Future Enhancements

### Near-term
- **Unit Tests**: Pytest for backend, Jest for frontend
- **Error Recovery**: Graceful handling of partial data
- **Export Functionality**: Download calculated results as CSV

### Long-term
- **Database Integration**: PostgreSQL for data persistence
- **Real-time Updates**: WebSocket for live price streaming
- **Multiple ETF Comparison**: Side-by-side analysis
- **Performance Metrics**: Calculate Sharpe ratio, volatility, etc.
- **Date Range Selection**: Custom time period filtering
- **Dockerization**: Container-based deployment

---

## Testing

To test the application:
1. Start the development server with `npm run dev`
2. Navigate to `http://localhost:3000`
3. Upload `data/ETF1.csv` or `data/ETF2.csv`
4. Verify:
   - Table displays all constituents with correct data
   - Time series chart shows ETF price from 2017-01-01 to 2017-04-10
   - Top 5 bar chart displays correct holdings sorted by value
   - All charts and tables are interactive
